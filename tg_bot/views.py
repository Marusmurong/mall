from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import TelegramBotSettings, TelegramNotification
import json
import requests

# Create your views here.

@csrf_exempt
@require_POST
def webhook(request):
    """
    处理来自Telegram的webhook请求
    """
    try:
        data = json.loads(request.body)
        # 这里可以添加处理Telegram消息的逻辑
        return JsonResponse({'status': 'ok'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def settings(request):
    """
    显示Telegram机器人设置页面
    """
    settings = TelegramBotSettings.objects.first()
    notifications = TelegramNotification.objects.all()[:10]
    context = {
        'settings': settings,
        'notifications': notifications,
    }
    return render(request, 'tg_bot/settings.html', context)
