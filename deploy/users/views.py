from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.urls import reverse
from django.http import Http404, JsonResponse
from django.utils import timezone
from datetime import timedelta

from .forms import RegisterForm, UserProfileForm
from .models import UserProfile, InvitationRecord
from .decorators import check_user_ban
from wishlist.models import Wishlist


def register_view(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 登录用户
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, '注册成功！欢迎加入我们的社区。')
            return redirect('users:profile')
    else:
        # 如果URL中有邀请码参数，预填充表单
        invite_code = request.GET.get('invite_code', '')
        initial_data = {}
        if invite_code:
            initial_data['invite_code'] = invite_code
        form = RegisterForm(initial=initial_data)
    
    return render(request, 'users/register.html', {'form': form})


@login_required
@check_user_ban
def profile_view(request):
    """用户资料页面"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '资料更新成功！')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    # 获取用户的邀请码和邀请链接
    invite_url = request.build_absolute_uri(
        reverse('users:register') + f'?invite_code={request.user.profile.invite_code}'
    )
    
    context = {
        'form': form,
        'invite_code': request.user.profile.invite_code,
        'invite_url': invite_url,
    }
    return render(request, 'users/profile.html', context)


@login_required
@check_user_ban
def invitation_network_view(request):
    """用户邀请网络页面"""
    # 获取当前用户邀请的用户树结构
    invitation_tree = request.user.profile.get_invitation_tree(max_depth=2)
    
    # 获取直接邀请的用户的信息
    direct_invitees = request.user.profile.get_direct_invitees()
    direct_invitee_data = []
    
    for invitee in direct_invitees:
        # 获取该用户的心愿单数量
        wishlist_count = Wishlist.objects.filter(user=invitee.user).count()
        
        # 获取该用户的心愿单成交情况
        # 此处假设心愿单有一个字段表示是否已成交，实际情况可能需要更复杂的逻辑
        # 这里暂时只统计心愿单总数
        
        invitee_data = {
            'user': invitee.user,
            'profile': invitee,
            'wishlist_count': wishlist_count,
            'invite_count': invitee.invitees.count(),
        }
        direct_invitee_data.append(invitee_data)
    
    context = {
        'invitation_tree': invitation_tree,
        'direct_invitees': direct_invitee_data,
        'invitee_count': request.user.profile.invitees.count(),
        'total_network_size': len(request.user.profile.get_all_invitees()),
    }
    return render(request, 'users/invitation_network.html', context)


@login_required
@check_user_ban
def invitee_detail_view(request, user_id):
    """查看被邀请人详情"""
    invitee_profile = get_object_or_404(UserProfile, user_id=user_id)
    
    # 检查权限：只能查看自己邀请链下的用户
    current_user_profile = request.user.profile
    all_invitees = current_user_profile.get_all_invitees()
    
    if invitee_profile not in all_invitees and invitee_profile != current_user_profile:
        raise Http404("您没有权限查看该用户信息")
    
    # 获取该用户的心愿单
    wishlists = Wishlist.objects.filter(user=invitee_profile.user)
    
    # 获取该用户邀请的用户
    invitees = invitee_profile.get_direct_invitees()
    
    context = {
        'profile': invitee_profile,
        'wishlists': wishlists,
        'invitees': invitees,
    }
    return render(request, 'users/invitee_detail.html', context)


def ban_notice_view(request):
    """封号提示页面"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    if not request.user.profile.is_banned:
        return redirect('users:profile')
    
    ban_info = {
        'reason': request.user.profile.ban_reason or '违反用户协议',
        'until': request.user.profile.ban_until,
        'is_permanent': request.user.profile.ban_until is None,
    }
    
    return render(request, 'users/ban_notice.html', {
        'ban_info': ban_info
    })


@user_passes_test(lambda u: u.is_staff)
def ban_user_view(request, user_id):
    """管理员封禁用户"""
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    
    # 不能封禁管理员
    if user_profile.user.is_staff:
        messages.error(request, '无法封禁管理员账号')
        return redirect('admin:auth_user_changelist')
    
    if request.method == 'POST':
        ban_reason = request.POST.get('ban_reason', '')
        ban_days = request.POST.get('ban_days', '')
        
        user_profile.is_banned = True
        user_profile.ban_reason = ban_reason
        user_profile.ban_count += 1
        user_profile.last_ban_time = timezone.now()
        
        # 如果指定了天数，设置临时封号，否则为永久封号
        if ban_days and ban_days.isdigit() and int(ban_days) > 0:
            user_profile.ban_until = timezone.now() + timedelta(days=int(ban_days))
        else:
            user_profile.ban_until = None  # 永久封号
        
        user_profile.save()
        
        messages.success(request, f'用户 {user_profile.user.username} 已被成功封禁')
        return redirect('admin:auth_user_changelist')
    
    return render(request, 'users/ban_user.html', {
        'user_profile': user_profile
    })


@user_passes_test(lambda u: u.is_staff)
def unban_user_view(request, user_id):
    """管理员解封用户"""
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    
    if not user_profile.is_banned:
        messages.info(request, f'用户 {user_profile.user.username} 未被封禁')
        return redirect('admin:auth_user_changelist')
    
    user_profile.is_banned = False
    user_profile.save(update_fields=['is_banned'])
    
    messages.success(request, f'用户 {user_profile.user.username} 已被成功解封')
    return redirect('admin:auth_user_changelist')


@user_passes_test(lambda u: u.is_staff)
def user_ban_status_api(request, user_id):
    """获取用户封禁状态的API"""
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        return JsonResponse({
            'is_banned': user_profile.is_banned,
            'ban_reason': user_profile.ban_reason,
            'ban_until': user_profile.ban_until.isoformat() if user_profile.ban_until else None,
            'ban_count': user_profile.ban_count,
            'last_ban_time': user_profile.last_ban_time.isoformat() if user_profile.last_ban_time else None,
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
