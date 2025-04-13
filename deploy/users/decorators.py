from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

def check_user_ban(view_func):
    """检查用户是否被封号的装饰器"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            profile = request.user.profile
            
            # 如果用户被封号
            if profile.is_banned:
                # 检查是否是临时封号并且已经到期
                if profile.ban_until and profile.ban_until < timezone.now():
                    # 解封账号
                    profile.is_banned = False
                    profile.save(update_fields=['is_banned'])
                else:
                    # 重定向到封号提示页面
                    messages.error(request, f'您的账号已被封禁，原因：{profile.ban_reason or "违反用户协议"}')
                    return redirect('ban_notice')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view 