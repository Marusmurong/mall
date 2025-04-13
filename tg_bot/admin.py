from django.contrib import admin
from .models import TelegramBotSettings, TelegramNotification

@admin.register(TelegramBotSettings)
class TelegramBotSettingsAdmin(admin.ModelAdmin):
    list_display = ('webhook_url', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('webhook_url',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TelegramNotification)
class TelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'message', 'sent_at', 'is_sent')
    list_filter = ('is_sent', 'sent_at')
    search_fields = ('chat_id', 'message')
    readonly_fields = ('sent_at',)
    ordering = ('-sent_at',)
