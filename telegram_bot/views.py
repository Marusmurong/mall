import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings
from users.decorators import check_user_ban

from .models import UserTelegramBinding, TelegramNotificationSettings
from .utils import generate_verification_code, send_telegram_message

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    """处理来自Telegram的Webhook请求"""
    try:
        data = json.loads(request.body)
        logger.info(f"收到Telegram更新: {data}")
        
        # 将消息处理委托给异步任务
        from .tasks import process_telegram_update
        process_telegram_update.delay(data)
        
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"处理Telegram webhook失败: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@check_user_ban
def telegram_settings(request):
    """用户Telegram绑定设置页面"""
    try:
        # 检查用户是否已经绑定Telegram
        binding = UserTelegramBinding.objects.filter(user=request.user).first()
        
        # 获取通知设置
        notification_settings = None
        if binding:
            notification_settings = TelegramNotificationSettings.objects.filter(user_binding=binding).first()
        
        if request.method == 'POST':
            if 'unbind_telegram' in request.POST and binding:
                # 解除绑定
                binding.delete()
                messages.success(request, _('成功解除Telegram绑定'))
                return redirect('telegram_bot:telegram_settings')
            
            elif 'update_notification_settings' in request.POST and notification_settings:
                # 更新通知设置
                notification_settings.notify_wishlist_view = 'notify_wishlist_view' in request.POST
                notification_settings.notify_wishlist_purchase = 'notify_wishlist_purchase' in request.POST
                notification_settings.notify_system_message = 'notify_system_message' in request.POST
                
                # 处理免打扰时间
                quiet_hours_start = request.POST.get('quiet_hours_start')
                quiet_hours_end = request.POST.get('quiet_hours_end')
                if quiet_hours_start and quiet_hours_end:
                    notification_settings.quiet_hours_start = quiet_hours_start
                    notification_settings.quiet_hours_end = quiet_hours_end
                else:
                    notification_settings.quiet_hours_start = None
                    notification_settings.quiet_hours_end = None
                
                notification_settings.save()
                messages.success(request, _('通知设置已更新'))
            
            elif 'generate_code' in request.POST and not binding:
                # 生成新的验证码
                verification_code = generate_verification_code()
                
                # 创建绑定记录（未验证）
                binding = UserTelegramBinding.objects.create(
                    user=request.user,
                    verification_code=verification_code,
                    telegram_id='',  # 此时还不知道telegram_id
                    verified=False
                )
                
                messages.success(request, _(f'验证码已生成: {verification_code}，请在Telegram机器人中使用此验证码完成绑定'))
                return redirect('telegram_bot:telegram_settings')
        
        # 准备Bot信息
        from .utils import get_bot_settings
        bot_settings = get_bot_settings()
        bot_username = bot_settings.bot_username if bot_settings else None
        
        context = {
            'binding': binding,
            'notification_settings': notification_settings,
            'bot_username': bot_username,
        }
        
        return render(request, 'telegram_bot/settings.html', context)
    except Exception as e:
        logger.error(f"访问Telegram设置页面失败: {str(e)}")
        messages.error(request, _('操作失败，请稍后再试'))
        return redirect('profile')


@login_required
@check_user_ban
def send_test_notification(request):
    """发送测试通知"""
    try:
        # 检查用户是否已绑定Telegram
        binding = get_object_or_404(UserTelegramBinding, user=request.user, verified=True)
        
        # 构建测试消息
        message = _("""
这是一条测试通知消息！

您的Telegram通知功能运行正常。
当您的心愿单有新动态时，您将收到类似的通知。

感谢您使用我们的服务！
        """).strip()
        
        # 发送测试消息
        result = send_telegram_message(binding.telegram_id, message)
        
        if result:
            messages.success(request, _('测试消息已发送至您的Telegram'))
        else:
            messages.error(request, _('发送测试消息失败，请确保您没有屏蔽机器人'))
        
        return redirect('telegram_bot:telegram_settings')
    except UserTelegramBinding.DoesNotExist:
        messages.error(request, _('您尚未绑定Telegram或绑定未验证'))
        return redirect('telegram_bot:telegram_settings')
    except Exception as e:
        logger.error(f"发送测试通知失败: {str(e)}")
        messages.error(request, _('操作失败，请稍后再试'))
        return redirect('telegram_bot:telegram_settings') 