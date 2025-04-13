import logging
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from wishlist.models import Wishlist, WishlistItem

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Wishlist)
def notify_wishlist_viewed(sender, instance, created, **kwargs):
    """当用户查看心愿单时发送通知"""
    if not created and hasattr(instance, '_viewer_id'):  # 只处理心愿单的查看，不处理创建
        viewer_id = instance._viewer_id
        
        # 使用Channels发送通知
        try:
            # 准备消息内容
            user_id = instance.user.id
            viewer_info = ""
            
            if viewer_id:
                try:
                    viewer = User.objects.get(id=viewer_id)
                    viewer_info = f"用户 {viewer.username} "
                except Exception:
                    pass
            
            message = f"""
📋 您的心愿单被查看了！

心愿单: <b>{instance.title}</b>
{viewer_info}刚刚查看了您的心愿单。

<a href="https://example.com/wishlist/{instance.id}/">点击查看心愿单详情</a>
            """
            
            # 发送到Channels
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "telegram_notifications",
                {
                    "type": "send_notification",
                    "user_id": user_id,
                    "notification_type": "wishlist_view",
                    "content": message,
                    "related_object_type": "wishlist",
                    "related_object_id": instance.id,
                }
            )
            
            logger.info(f"已发送心愿单查看通知: 用户 {user_id}, 心愿单 {instance.id}, 查看者 {viewer_id}")
        except Exception as e:
            logger.error(f"发送心愿单查看通知失败: {str(e)}")


@receiver(post_save, sender=WishlistItem)
def notify_wishlist_item_purchased(sender, instance, created, **kwargs):
    """当心愿单物品被购买时发送通知"""
    # 检查物品是否被购买
    if not created and instance.purchased and hasattr(instance, '_previous_purchased'):
        if not instance._previous_purchased:  # 状态变更为已购买
            buyer_id = getattr(instance, '_buyer_id', None)
            
            # 使用Channels发送通知
            try:
                # 准备消息内容
                user_id = instance.wishlist.user.id
                buyer_info = ""
                
                if buyer_id:
                    try:
                        buyer = User.objects.get(id=buyer_id)
                        buyer_info = f"用户 {buyer.username} "
                    except Exception:
                        pass
                
                message = f"""
🎁 您的心愿单物品已被购买！

物品: <b>{instance.title}</b>
价格: {instance.price}
心愿单: {instance.wishlist.title}

{buyer_info}已完成了此物品的购买。

<a href="https://example.com/wishlist/{instance.wishlist.id}/">点击查看心愿单详情</a>
                """
                
                # 发送到Channels
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "telegram_notifications",
                    {
                        "type": "send_notification",
                        "user_id": user_id,
                        "notification_type": "wishlist_purchase",
                        "content": message,
                        "related_object_type": "wishlist_item",
                        "related_object_id": instance.id,
                    }
                )
                
                logger.info(f"已发送心愿单物品购买通知: 用户 {user_id}, 物品 {instance.id}, 购买者 {buyer_id}")
            except Exception as e:
                logger.error(f"发送心愿单物品购买通知失败: {str(e)}") 