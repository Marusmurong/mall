import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import UserTelegramBinding

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """处理Telegram通知的WebSocket消费者"""
    
    async def connect(self):
        """WebSocket连接建立"""
        # 添加到通知组
        await self.channel_layer.group_add(
            "telegram_notifications",
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket连接已建立: {self.channel_name}")
    
    async def disconnect(self, close_code):
        """WebSocket连接断开"""
        # 从通知组中移除
        await self.channel_layer.group_discard(
            "telegram_notifications",
            self.channel_name
        )
        logger.info(f"WebSocket连接已断开: {self.channel_name}, 代码: {close_code}")
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            logger.info(f"收到WebSocket消息: {data}")
            
            message_type = data.get('type')
            if message_type == 'send_notification':
                await self.handle_send_notification(data)
        except Exception as e:
            logger.error(f"处理WebSocket消息时出错: {str(e)}")
    
    async def send_notification(self, event):
        """处理通知发送事件"""
        try:
            user_id = event.get('user_id')
            notification_type = event.get('notification_type')
            content = event.get('content')
            related_object_type = event.get('related_object_type', '')
            related_object_id = event.get('related_object_id')
            
            if not user_id or not notification_type or not content:
                logger.error(f"缺少必要参数: {event}")
                return
            
            # 异步获取用户Telegram绑定
            binding = await self.get_user_telegram_binding(user_id)
            if not binding:
                logger.info(f"用户 {user_id} 未绑定Telegram或绑定未激活")
                return
            
            # 异步检查是否应该发送此类型的通知
            if not await self.should_send_notification(binding, notification_type):
                logger.info(f"用户 {user_id} 已禁用 {notification_type} 类型的通知")
                return
            
            # 创建通知记录
            notification = await self.create_notification(
                binding, notification_type, content, related_object_type, related_object_id
            )
            
            if notification:
                # 异步发送Telegram消息
                success, error = await self.send_telegram_message(binding.telegram_id, content)
                
                if success:
                    # 更新通知状态为已发送
                    await self.mark_notification_sent(notification.id)
                    
                    # 向通知组广播结果
                    await self.channel_layer.group_send(
                        "telegram_notifications",
                        {
                            'type': 'telegram_notification',
                            'status': 'sent',
                            'message': '通知已发送',
                            'user_id': user_id,
                            'notification_id': notification.id,
                        }
                    )
                else:
                    # 更新通知状态为发送失败
                    await self.mark_notification_failed(notification.id, error)
                    
                    # 向通知组广播结果
                    await self.channel_layer.group_send(
                        "telegram_notifications",
                        {
                            'type': 'telegram_notification',
                            'status': 'failed',
                            'message': f'发送失败: {error}',
                            'user_id': user_id,
                            'notification_id': notification.id,
                        }
                    )
        except Exception as e:
            logger.error(f"处理通知发送事件失败: {str(e)}")
    
    async def telegram_notification(self, event):
        """向WebSocket客户端发送通知状态更新"""
        await self.send(text_data=json.dumps({
            'type': 'telegram_notification',
            'status': event.get('status'),
            'message': event.get('message'),
            'user_id': event.get('user_id'),
            'notification_id': event.get('notification_id'),
        }))
    
    async def handle_send_notification(self, data):
        """处理发送通知请求"""
        user_id = data.get('user_id')
        notification_type = data.get('notification_type')
        content = data.get('content')
        related_object_type = data.get('related_object_type', '')
        related_object_id = data.get('related_object_id')
        
        if not user_id or not notification_type or not content:
            logger.error(f"缺少必要参数: {data}")
            return
        
        # 异步获取用户Telegram绑定
        binding = await self.get_user_telegram_binding(user_id)
        if not binding:
            logger.info(f"用户 {user_id} 未绑定Telegram或绑定未激活")
            return
        
        # 异步检查是否应该发送此类型的通知
        if not await self.should_send_notification(binding, notification_type):
            logger.info(f"用户 {user_id} 已禁用 {notification_type} 类型的通知")
            return
        
        # 创建通知记录
        notification = await self.create_notification(
            binding, notification_type, content, related_object_type, related_object_id
        )
        
        if notification:
            # 异步发送Telegram消息
            success, error = await self.send_telegram_message(binding.telegram_id, content)
            
            if success:
                # 更新通知状态为已发送
                await self.mark_notification_sent(notification.id)
                
                # 向通知组广播结果
                await self.channel_layer.group_send(
                    "telegram_notifications",
                    {
                        'type': 'telegram_notification',
                        'status': 'sent',
                        'message': '通知已发送',
                        'user_id': user_id,
                        'notification_id': notification.id,
                    }
                )
            else:
                # 更新通知状态为发送失败
                await self.mark_notification_failed(notification.id, error)
                
                # 向通知组广播结果
                await self.channel_layer.group_send(
                    "telegram_notifications",
                    {
                        'type': 'telegram_notification',
                        'status': 'failed',
                        'message': f'发送失败: {error}',
                        'user_id': user_id,
                        'notification_id': notification.id,
                    }
                )
    
    @database_sync_to_async
    def get_user_telegram_binding(self, user_id):
        """异步获取用户的Telegram绑定"""
        try:
            return UserTelegramBinding.objects.get(
                user_id=user_id,
                verified=True,
                is_active=True
            )
        except UserTelegramBinding.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"获取用户Telegram绑定失败: {str(e)}")
            return None
    
    @database_sync_to_async
    def should_send_notification(self, binding, notification_type):
        """异步检查是否应该发送此类型的通知"""
        try:
            from .utils import can_send_notification
            if not can_send_notification(binding):
                return False
                
            settings = binding.notification_settings
            if notification_type == 'wishlist_view' and not settings.notify_wishlist_view:
                return False
            if notification_type == 'wishlist_purchase' and not settings.notify_wishlist_purchase:
                return False
            if notification_type == 'system' and not settings.notify_system_message:
                return False
            
            return True
        except Exception as e:
            logger.error(f"检查通知设置失败: {str(e)}")
            return True  # 默认允许发送
    
    @database_sync_to_async
    def create_notification(self, binding, notification_type, content, related_object_type='', related_object_id=None):
        """异步创建通知记录"""
        try:
            from .models import TelegramNotification
            notification = TelegramNotification.objects.create(
                user_binding=binding,
                notification_type=notification_type,
                content=content,
                related_object_type=related_object_type,
                related_object_id=related_object_id
            )
            return notification
        except Exception as e:
            logger.error(f"创建通知记录失败: {str(e)}")
            return None
    
    @database_sync_to_async
    def mark_notification_sent(self, notification_id):
        """异步标记通知为已发送"""
        try:
            from .models import TelegramNotification
            notification = TelegramNotification.objects.get(id=notification_id)
            notification.mark_as_sent()
            return True
        except Exception as e:
            logger.error(f"标记通知为已发送失败: {str(e)}")
            return False
    
    @database_sync_to_async
    def mark_notification_failed(self, notification_id, error_message):
        """异步标记通知为发送失败"""
        try:
            from .models import TelegramNotification
            notification = TelegramNotification.objects.get(id=notification_id)
            notification.mark_as_failed(error_message)
            return True
        except Exception as e:
            logger.error(f"标记通知为发送失败失败: {str(e)}")
            return False
    
    @database_sync_to_async
    def send_telegram_message(self, chat_id, text):
        """异步发送Telegram消息"""
        try:
            from .utils import send_telegram_message
            result = send_telegram_message(chat_id, text)
            if result:
                return True, None
            return False, "发送消息失败"
        except Exception as e:
            logger.error(f"发送Telegram消息失败: {str(e)}")
            return False, str(e) 