from django.contrib import admin
from django.utils.html import format_html
from .models import (
    TelegramBotSettings, 
    UserTelegramBinding, 
    TelegramNotificationSettings,
    TelegramNotification
)

# 创建别名
TelegramConfig = TelegramBotSettings

class TelegramConfigAdmin(admin.ModelAdmin):
    list_display = ('bot_username', 'is_active', 'webhook_url', 'updated_at')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本设置', {
            'fields': ('bot_token', 'bot_username', 'is_active')
        }),
        ('Webhook配置', {
            'fields': ('webhook_url',),
            'classes': ('collapse',),
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 如果激活了Bot，则设置webhook
        if obj.is_active and obj.bot_token:
            from .utils import setup_telegram_webhook
            setup_telegram_webhook(obj)

# 使用别名注册
admin.site.register(TelegramConfig, TelegramConfigAdmin)

@admin.register(UserTelegramBinding)
class UserTelegramBindingAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_username', 'telegram_id', 'verified', 'is_active', 'created_at')
    list_filter = ('verified', 'is_active')
    search_fields = ('user__username', 'telegram_username', 'telegram_id')
    readonly_fields = ('telegram_id', 'telegram_username', 'telegram_first_name', 
                       'telegram_last_name', 'verification_code', 'verified', 
                       'created_at', 'updated_at')
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'is_active')
        }),
        ('Telegram信息', {
            'fields': ('telegram_id', 'telegram_username', 'telegram_first_name', 'telegram_last_name')
        }),
        ('验证信息', {
            'fields': ('verification_code', 'verified')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(TelegramNotificationSettings)
class TelegramNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'notify_wishlist_view', 'notify_wishlist_purchase', 
                   'notify_system_message', 'get_quiet_hours')
    list_filter = ('notify_wishlist_view', 'notify_wishlist_purchase', 'notify_system_message')
    search_fields = ('user_binding__user__username', 'user_binding__telegram_username')
    
    def get_username(self, obj):
        return obj.user_binding.user.username
    get_username.short_description = '用户'
    
    def get_quiet_hours(self, obj):
        if obj.quiet_hours_start and obj.quiet_hours_end:
            return f"{obj.quiet_hours_start.strftime('%H:%M')} - {obj.quiet_hours_end.strftime('%H:%M')}"
        return '未设置'
    get_quiet_hours.short_description = '免打扰时间'


@admin.register(TelegramNotification)
class TelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'notification_type', 'status', 
                   'get_content_preview', 'created_at', 'sent_at')
    list_filter = ('notification_type', 'status', 'created_at')
    search_fields = ('user_binding__user__username', 'content')
    readonly_fields = ('user_binding', 'notification_type', 'content', 
                      'related_object_id', 'related_object_type', 
                      'status', 'error_message', 'created_at', 'sent_at')
    fieldsets = (
        ('通知信息', {
            'fields': ('user_binding', 'notification_type', 'content')
        }),
        ('关联对象', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',),
        }),
        ('状态信息', {
            'fields': ('status', 'error_message', 'created_at', 'sent_at')
        }),
    )
    actions = ['resend_notifications']
    
    def get_username(self, obj):
        return obj.user_binding.user.username
    get_username.short_description = '用户'
    
    def get_content_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    get_content_preview.short_description = '内容预览'
    
    def resend_notifications(self, request, queryset):
        from .tasks import send_telegram_notification
        count = 0
        for notification in queryset.filter(status='failed'):
            send_telegram_notification.delay(notification.id)
            count += 1
        self.message_user(request, f'已重新发送 {count} 条通知')
    resend_notifications.short_description = '重新发送失败通知' 