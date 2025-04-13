import logging
import random
import string
import requests
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)

# Telegram Bot API基础URL
TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def get_bot_settings():
    """获取机器人配置"""
    from .models import TelegramBotSettings
    try:
        return TelegramBotSettings.objects.filter(is_active=True).first()
    except Exception as e:
        logger.error(f"获取Telegram Bot设置失败: {str(e)}")
        return None


def setup_telegram_webhook(bot_settings):
    """设置Telegram Bot Webhook"""
    if not bot_settings or not bot_settings.bot_token:
        logger.error("未配置Bot Token，无法设置webhook")
        return False
    
    # 生成Webhook URL
    webhook_url = generate_webhook_url()
    
    # 请求Telegram API设置webhook
    api_url = f"{TELEGRAM_API_BASE}{bot_settings.bot_token}/setWebhook"
    try:
        response = requests.post(api_url, json={
            'url': webhook_url,
            'allowed_updates': ['message', 'callback_query']
        })
        
        if response.status_code == 200 and response.json().get('ok'):
            # 保存webhook_url到配置
            bot_settings.webhook_url = webhook_url
            bot_settings.save(update_fields=['webhook_url'])
            logger.info(f"成功设置Telegram webhook: {webhook_url}")
            return True
        else:
            logger.error(f"设置webhook失败: {response.text}")
            return False
    except Exception as e:
        logger.error(f"请求Telegram API失败: {str(e)}")
        return False


def generate_webhook_url():
    """生成Webhook URL"""
    # 强制设置为ngrok URL
    base_url = "https://7a77-60-48-150-169.ngrok-free.app"
    
    webhook_path = reverse('telegram_bot:webhook')
    return f"{base_url}{webhook_path}"


def generate_verification_code(length=6):
    """生成验证码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def send_telegram_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    """发送Telegram消息"""
    bot_settings = get_bot_settings()
    if not bot_settings or not bot_settings.bot_token:
        logger.error("未配置Bot Token，无法发送消息")
        return False
    
    api_url = f"{TELEGRAM_API_BASE}{bot_settings.bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200 and response.json().get('ok'):
            return response.json().get('result')
        else:
            logger.error(f"发送消息失败: {response.text}")
            return False
    except Exception as e:
        logger.error(f"请求Telegram API失败: {str(e)}")
        return False


def can_send_notification(user_binding):
    """检查是否可以向用户发送通知"""
    if not user_binding or not user_binding.is_active or not user_binding.verified:
        return False
    
    # 检查通知设置
    try:
        settings = user_binding.notification_settings
        if settings.quiet_hours_start and settings.quiet_hours_end:
            current_time = timezone.localtime().time()
            
            # 处理跨午夜的免打扰时间
            if settings.quiet_hours_start > settings.quiet_hours_end:
                # 例如22:00-06:00的情况
                if current_time >= settings.quiet_hours_start or current_time <= settings.quiet_hours_end:
                    return False
            else:
                # 例如00:00-06:00的情况
                if settings.quiet_hours_start <= current_time <= settings.quiet_hours_end:
                    return False
        
        return True
    except Exception as e:
        logger.error(f"检查通知设置失败: {str(e)}")
        return True  # 如果无法检查，默认允许发送


def create_notification(user_binding, notification_type, content, related_object_type=None, related_object_id=None):
    """创建通知记录"""
    from .models import TelegramNotification
    
    if not user_binding or not user_binding.verified:
        return None
    
    # 检查是否应该发送此类型的通知
    try:
        settings = user_binding.notification_settings
        if notification_type == 'wishlist_view' and not settings.notify_wishlist_view:
            return None
        if notification_type == 'wishlist_purchase' and not settings.notify_wishlist_purchase:
            return None
        if notification_type == 'system' and not settings.notify_system_message:
            return None
    except Exception:
        # 如果获取设置失败，使用默认设置
        pass
    
    # 创建通知记录
    try:
        notification = TelegramNotification.objects.create(
            user_binding=user_binding,
            notification_type=notification_type,
            content=content,
            related_object_type=related_object_type or '',
            related_object_id=related_object_id
        )
        return notification
    except Exception as e:
        logger.error(f"创建通知记录失败: {str(e)}")
        return None 