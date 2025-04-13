from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'
    verbose_name = 'Telegram机器人'

    def ready(self):
        import telegram_bot.signals  # 导入信号处理模块 