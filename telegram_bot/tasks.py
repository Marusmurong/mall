import logging
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.urls import reverse
from celery import shared_task

from .models import (
    TelegramBotSettings, 
    UserTelegramBinding, 
    TelegramNotificationSettings,
    TelegramNotification
)
from .utils import send_telegram_message, can_send_notification, generate_verification_code

logger = logging.getLogger(__name__)


@shared_task
def send_telegram_notification(notification_id):
    """异步发送Telegram消息"""
    try:
        notification = TelegramNotification.objects.get(id=notification_id)
        
        # 检查是否可以发送通知
        if not can_send_notification(notification.user_binding):
            notification.mark_as_failed("用户在免打扰时间段或通知已禁用")
            return False
        
        # 发送消息
        result = send_telegram_message(
            notification.user_binding.telegram_id,
            notification.content
        )
        
        if result:
            notification.mark_as_sent()
            return True
        else:
            notification.mark_as_failed("发送消息失败")
            return False
            
    except ObjectDoesNotExist:
        logger.error(f"通知记录不存在: {notification_id}")
        return False
    except Exception as e:
        logger.error(f"发送通知失败: {str(e)}")
        try:
            notification.mark_as_failed(str(e))
        except:
            pass
        return False


@shared_task
def process_telegram_update(update_data):
    """处理来自Telegram的更新"""
    try:
        # 处理消息类型的更新
        if 'message' in update_data:
            process_message(update_data['message'])
        
        # 处理回调查询
        elif 'callback_query' in update_data:
            process_callback_query(update_data['callback_query'])
        
        return True
    except Exception as e:
        logger.error(f"处理Telegram更新失败: {str(e)}")
        return False


def process_message(message):
    """处理Telegram消息"""
    try:
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        if not chat_id or not text:
            return
        
        # 检查是否是/start命令
        if text.startswith('/start'):
            handle_start_command(chat_id, message)
        
        # 检查是否是/bind命令或验证码
        elif text.startswith('/bind') or (len(text) == 6 and text.isalnum()):
            handle_bind_command(chat_id, message, text)
        
        # 其他命令处理...
        
    except Exception as e:
        logger.error(f"处理Telegram消息失败: {str(e)}")


def handle_start_command(chat_id, message):
    """处理/start命令"""
    from_user = message.get('from', {})
    
    welcome_message = """
欢迎使用心愿单通知机器人！

此机器人可以在您的心愿单有活动时通知您，如被查看、商品被购买等。

要使用此功能，请按以下步骤操作：
1. 在网站个人设置中生成绑定码
2. 将绑定码发送给我或使用 /bind 命令加上绑定码

例如: /bind ABC123 或直接发送 ABC123

需要帮助？请使用 /help 命令查看更多信息。
    """
    
    send_telegram_message(chat_id, welcome_message)


def handle_bind_command(chat_id, message, text):
    """处理绑定命令或验证码"""
    from_user = message.get('from', {})
    telegram_id = str(from_user.get('id', ''))
    telegram_username = from_user.get('username', '')
    telegram_first_name = from_user.get('first_name', '')
    telegram_last_name = from_user.get('last_name', '')
    
    # 提取验证码
    if text.startswith('/bind'):
        parts = text.split()
        if len(parts) < 2:
            send_telegram_message(chat_id, "请提供绑定码，格式: /bind 您的绑定码")
            return
        verification_code = parts[1].strip().upper()
    else:
        verification_code = text.strip().upper()
    
    # 查找绑定记录
    try:
        binding = UserTelegramBinding.objects.get(
            verification_code=verification_code,
            verified=False
        )
        
        # 更新绑定信息
        binding.telegram_id = telegram_id
        binding.telegram_username = telegram_username
        binding.telegram_first_name = telegram_first_name
        binding.telegram_last_name = telegram_last_name
        binding.verified = True
        binding.save()
        
        # 创建通知设置
        TelegramNotificationSettings.objects.get_or_create(user_binding=binding)
        
        send_telegram_message(chat_id, f"""
绑定成功！您的账号 {binding.user.username} 已成功绑定到Telegram。

现在您将收到心愿单相关的通知。
您可以随时在网站的个人设置中管理通知选项或解除绑定。

感谢您使用我们的服务！
        """)
        
    except UserTelegramBinding.DoesNotExist:
        send_telegram_message(chat_id, "绑定码无效或已过期，请在网站上重新生成绑定码")
    except Exception as e:
        logger.error(f"处理绑定命令失败: {str(e)}")
        send_telegram_message(chat_id, "绑定过程中出现错误，请稍后重试")


def process_callback_query(callback_query):
    """处理回调查询"""
    try:
        # 暂未实现回调按钮功能
        pass
    except Exception as e:
        logger.error(f"处理回调查询失败: {str(e)}")


@shared_task
def notify_wishlist_viewed(wishlist_id, viewer_id=None):
    """通知心愿单被查看"""
    from wishlist.models import Wishlist
    
    try:
        wishlist = Wishlist.objects.select_related('user').get(id=wishlist_id)
        
        # 查找用户绑定
        try:
            binding = UserTelegramBinding.objects.get(
                user=wishlist.user,
                verified=True,
                is_active=True
            )
            
            # 检查是否需要发送此类通知
            settings = binding.notification_settings
            if not settings.notify_wishlist_view:
                return
                
            # 准备消息内容
            viewer_info = ""
            if viewer_id:
                try:
                    viewer = User.objects.get(id=viewer_id)
                    viewer_info = f"用户 {viewer.username} "
                except:
                    pass
            
            message = f"""
📋 您的心愿单被查看了！

心愿单: <b>{wishlist.title}</b>
{viewer_info}刚刚查看了您的心愿单。

<a href="https://example.com/wishlist/{wishlist.id}/">点击查看心愿单详情</a>
            """
            
            # 创建通知记录
            notification = TelegramNotification.objects.create(
                user_binding=binding,
                notification_type='wishlist_view',
                content=message,
                related_object_type='wishlist',
                related_object_id=wishlist.id
            )
            
            # 发送通知
            send_telegram_notification.delay(notification.id)
            
        except UserTelegramBinding.DoesNotExist:
            # 用户未绑定Telegram，不发送通知
            pass
            
    except Wishlist.DoesNotExist:
        logger.error(f"心愿单不存在: {wishlist_id}")
    except Exception as e:
        logger.error(f"通知心愿单被查看失败: {str(e)}")


@shared_task
def notify_wishlist_item_purchased(wishlist_item_id, buyer_id=None):
    """通知心愿单物品被购买"""
    from wishlist.models import WishlistItem
    
    try:
        item = WishlistItem.objects.select_related('wishlist__user').get(id=wishlist_item_id)
        
        # 查找用户绑定
        try:
            binding = UserTelegramBinding.objects.get(
                user=item.wishlist.user,
                verified=True,
                is_active=True
            )
            
            # 检查是否需要发送此类通知
            settings = binding.notification_settings
            if not settings.notify_wishlist_purchase:
                return
                
            # 准备购买者信息
            buyer_info = ""
            if buyer_id:
                try:
                    buyer = User.objects.get(id=buyer_id)
                    buyer_info = f"用户 {buyer.username} "
                except:
                    pass
            
            message = f"""
🎁 您的心愿单物品已被购买！

物品: <b>{item.title}</b>
价格: {item.price}
心愿单: {item.wishlist.title}

{buyer_info}已完成了此物品的购买。

<a href="https://example.com/wishlist/{item.wishlist.id}/">点击查看心愿单详情</a>
            """
            
            # 创建通知记录
            notification = TelegramNotification.objects.create(
                user_binding=binding,
                notification_type='wishlist_purchase',
                content=message,
                related_object_type='wishlist_item',
                related_object_id=item.id
            )
            
            # 发送通知
            send_telegram_notification.delay(notification.id)
            
        except UserTelegramBinding.DoesNotExist:
            # 用户未绑定Telegram，不发送通知
            pass
            
    except WishlistItem.DoesNotExist:
        logger.error(f"心愿单物品不存在: {wishlist_item_id}")
    except Exception as e:
        logger.error(f"通知心愿单物品被购买失败: {str(e)}") 