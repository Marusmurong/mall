from django.urls import path
from . import views

app_name = 'tg_bot'

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('settings/', views.settings, name='settings'),
] 