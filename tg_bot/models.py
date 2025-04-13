from django.db import models
from django.utils import timezone

class TelegramBotSettings(models.Model):
    bot_token = models.CharField(max_length=100, verbose_name='Bot Token')
    webhook_url = models.URLField(verbose_name='Webhook URL')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = 'Telegram机器人配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'Bot配置 ({self.webhook_url})'

class TelegramNotification(models.Model):
    chat_id = models.CharField(max_length=100, verbose_name='聊天ID')
    message = models.TextField(verbose_name='消息内容')
    sent_at = models.DateTimeField(default=timezone.now, verbose_name='发送时间')
    is_sent = models.BooleanField(default=False, verbose_name='是否已发送')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')

    class Meta:
        verbose_name = 'Telegram消息记录'
        verbose_name_plural = verbose_name
        ordering = ['-sent_at']

    def __str__(self):
        return f'消息 {self.sent_at.strftime("%Y-%m-%d %H:%M:%S")}'
