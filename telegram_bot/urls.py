from django.urls import path
from . import views

app_name = 'telegram_bot'

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('settings/', views.telegram_settings, name='telegram_settings'),
    path('test-notification/', views.send_test_notification, name='test_notification'),
] 