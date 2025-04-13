from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import UserProfile


class TelegramBotSettings(models.Model):
    """Telegram机器人全局设置"""
    bot_token = models.CharField(max_length=100, verbose_name="Bot Token")
    bot_username = models.CharField(max_length=100, verbose_name="Bot 用户名", blank=True)
    is_active = models.BooleanField(default=False, verbose_name="是否激活")
    webhook_url = models.URLField(blank=True, verbose_name="Webhook URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"Telegram Bot: {self.bot_username or '未设置'} ({'激活' if self.is_active else '未激活'})"
    
    class Meta:
        verbose_name = "Telegram机器人设置"
        verbose_name_plural = verbose_name


class UserTelegramBinding(models.Model):
    """用户与Telegram的绑定关系"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='telegram_binding', verbose_name="用户")
    telegram_id = models.CharField(max_length=50, unique=True, verbose_name="Telegram ID")
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name="Telegram用户名")
    telegram_first_name = models.CharField(max_length=100, blank=True, verbose_name="Telegram名")
    telegram_last_name = models.CharField(max_length=100, blank=True, verbose_name="Telegram姓")
    is_active = models.BooleanField(default=True, verbose_name="是否启用通知")
    verification_code = models.CharField(max_length=20, blank=True, verbose_name="验证码")
    verified = models.BooleanField(default=False, verbose_name="是否已验证")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.user.username} - {self.telegram_username or self.telegram_id}"
    
    class Meta:
        verbose_name = "用户Telegram绑定"
        verbose_name_plural = verbose_name


class TelegramNotificationSettings(models.Model):
    """用户Telegram通知设置"""
    user_binding = models.OneToOneField(UserTelegramBinding, on_delete=models.CASCADE, 
                                    related_name='notification_settings', verbose_name="绑定关系")
    notify_wishlist_view = models.BooleanField(default=True, verbose_name="心愿单被查看通知")
    notify_wishlist_purchase = models.BooleanField(default=True, verbose_name="心愿单物品购买通知")
    notify_system_message = models.BooleanField(default=True, verbose_name="系统消息通知")
    quiet_hours_start = models.TimeField(null=True, blank=True, verbose_name="免打扰开始时间")
    quiet_hours_end = models.TimeField(null=True, blank=True, verbose_name="免打扰结束时间")
    
    def __str__(self):
        return f"{self.user_binding.user.username}的通知设置"
    
    class Meta:
        verbose_name = "Telegram通知设置"
        verbose_name_plural = verbose_name


class TelegramNotification(models.Model):
    """Telegram通知记录"""
    TYPE_CHOICES = (
        ('wishlist_view', '心愿单被查看'),
        ('wishlist_purchase', '心愿单物品购买'),
        ('system', '系统消息'),
    )
    
    STATUS_CHOICES = (
        ('pending', '待发送'),
        ('sent', '已发送'),
        ('failed', '发送失败'),
    )
    
    user_binding = models.ForeignKey(UserTelegramBinding, on_delete=models.CASCADE, 
                                 related_name='notifications', verbose_name="绑定关系")
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="通知类型")
    content = models.TextField(verbose_name="通知内容")
    related_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="关联对象ID")
    related_object_type = models.CharField(max_length=50, blank=True, verbose_name="关联对象类型")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="发送时间")
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
    
    def mark_as_failed(self, error_message):
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user_binding.user.username}"
    
    class Meta:
        verbose_name = "Telegram通知记录"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


# 为了与admin URL匹配，创建别名
TelegramMessage = TelegramNotification

# 为了与admin URL匹配，创建别名
TelegramConfig = TelegramBotSettings 