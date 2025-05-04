from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html, escape
from django.utils import timezone
from django.db.models import Count
from .models import UserProfile, InvitationRecord, ShippingAddress

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'
    fields = ('bio', 'invite_code', 'inviter', 'is_banned', 'ban_reason', 'ban_until', 'ban_count')
    readonly_fields = ('invite_code', 'inviter', 'ban_count')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'date_joined', 'is_staff', 'get_invite_code', 
                   'get_referrer', 'get_invitee_count', 'get_invitee_accepted_count', 'get_ban_status', 'ban_actions')
    list_filter = ('profile__is_banned', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'profile__invite_code', 'profile__referrer__user__username')
    
    def get_invite_code(self, obj):
        return obj.profile.invite_code
    get_invite_code.short_description = '邀请码'
    
    def get_referrer(self, obj):
        if obj.profile.inviter:
            return obj.profile.inviter.user.username
        return '-'
    get_referrer.short_description = '邀请人'
    
    def get_invitee_count(self, obj):
        return obj.profile.invitees.count()
    get_invitee_count.short_description = '邀请用户数'
    
    def get_invitee_accepted_count(self, obj):
        return InvitationRecord.objects.filter(inviter=obj.profile, status='accepted').count()
    get_invitee_accepted_count.short_description = '成功注册用户数'
    
    def get_ban_status(self, obj):
        if not obj.profile.is_banned:
            return format_html('<span style="color: green;">正常</span>')
        
        if obj.profile.ban_until:
            # 临时封禁
            return format_html(
                '<span style="color: orange;">临时封禁至 {}</span>',
                obj.profile.ban_until.strftime('%Y-%m-%d %H:%M')
            )
        # 永久封禁
        return format_html('<span style="color: red;">永久封禁</span>')
    get_ban_status.short_description = '封禁状态'
    
    def ban_actions(self, obj):
        if obj.is_staff:
            return "管理员账号"
        
        if obj.profile.is_banned:
            url = reverse('users:unban_user', args=[obj.id])
            return format_html(
                '<a href="{}" class="button" style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;">解除封禁</a>',
                url
            )
        else:
            url = reverse('users:ban_user', args=[obj.id])
            return format_html(
                '<a href="{}" class="button" style="background-color: #ff4d4d; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;">封禁用户</a>',
                url
            )
    ban_actions.short_description = '操作'

# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(InvitationRecord)
class InvitationRecordAdmin(admin.ModelAdmin):
    list_display = ('inviter', 'invitee', 'invite_code', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('inviter__user__username', 'invitee__user__username', 'invite_code')
    readonly_fields = ('inviter', 'invitee', 'invite_code', 'created_at')

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'user', 'province', 'city', 'district', 'phone', 'is_default', 'created_at')
    list_filter = ('is_default', 'province', 'created_at')
    search_fields = ('recipient_name', 'user__username', 'phone', 'address', 'province', 'city', 'district')
    fieldsets = (
        ('基本信息', {
            'fields': (('user', 'is_default'), ('recipient_name', 'phone'))
        }),
        ('地址信息', {
            'fields': (('province', 'city', 'district'), 'address', 'postal_code')
        }),
        ('时间信息', {
            'fields': (('created_at', 'updated_at'),)
        })
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        """管理员可以编辑地址，但不能更改所属用户"""
        if obj:
            return self.readonly_fields + ('user',)
        return self.readonly_fields
