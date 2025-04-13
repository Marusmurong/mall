from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

class UserBanMiddleware:
    """用户封号检查中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 只检查已登录用户
        if request.user.is_authenticated:
            # 管理员不受封号限制
            if not request.user.is_staff:
                profile = request.user.profile
                
                # 如果用户被封号
                if profile.is_banned:
                    # 检查是否是临时封号并且已经到期
                    if profile.ban_until and profile.ban_until < timezone.now():
                        # 解封账号
                        profile.is_banned = False
                        profile.save(update_fields=['is_banned'])
                    else:
                        # 如果用户没有访问封号提示页面，则重定向到封号提示页面
                        if request.path != reverse('ban_notice'):
                            # 注销当前用户，但保留session以便在ban_notice页面显示封号信息
                            messages.error(request, f'您的账号已被封禁，原因：{profile.ban_reason or "违反用户协议"}')
                            return redirect('ban_notice')
        
        response = self.get_response(request)
        return response 