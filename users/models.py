from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """用户资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    invite_code = models.CharField(max_length=12, unique=True, blank=True, verbose_name='邀请码')
    inviter = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='invitees', verbose_name='邀请人')
    level = models.PositiveIntegerField(default=0, verbose_name='级别')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_banned = models.BooleanField(default=False, verbose_name='是否封号')
    ban_reason = models.CharField(max_length=255, blank=True, verbose_name='封号原因')
    ban_until = models.DateTimeField(null=True, blank=True, verbose_name='封号截止时间')
    ban_count = models.PositiveIntegerField(default=0, verbose_name='封号次数')
    last_ban_time = models.DateTimeField(null=True, blank=True, verbose_name='最近封号时间')
    
    # Telegram相关字段
    telegram_connected = models.BooleanField(default=False, verbose_name='是否绑定Telegram')
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name='Telegram用户名')
    telegram_chat_id = models.CharField(max_length=100, blank=True, verbose_name='Telegram聊天ID')
    telegram_token = models.CharField(max_length=100, blank=True, verbose_name='Telegram绑定令牌')
    telegram_token_created_at = models.DateTimeField(null=True, blank=True, verbose_name='令牌创建时间')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的资料"
    
    def save(self, *args, **kwargs):
        # 如果没有邀请码，则生成一个唯一的邀请码
        if not self.invite_code:
            while True:
                code = get_random_string(8).upper()
                if not UserProfile.objects.filter(invite_code=code).exists():
                    self.invite_code = code
                    break
        
        # 设置用户级别（直接下级为1，下下级为2，以此类推）
        if self.inviter:
            self.level = self.inviter.level + 1
        
        super().save(*args, **kwargs)
    
    def get_invite_url(self):
        """获取邀请链接"""
        return reverse('register') + f'?invite_code={self.invite_code}'
    
    def get_direct_invitees(self):
        """获取直接邀请的用户"""
        return self.invitees.all()
    
    def get_all_invitees(self):
        """获取所有邀请链下的用户（递归）"""
        all_invitees = list(self.invitees.all())
        for invitee in self.invitees.all():
            all_invitees.extend(invitee.get_all_invitees())
        return all_invitees
    
    def get_invitation_tree(self, level=0, max_depth=2):
        """获取邀请树结构（默认深度为2级）"""
        if level >= max_depth:
            return []
        
        result = []
        for invitee in self.invitees.all():
            invitee_data = {
                'user': invitee.user,
                'profile': invitee,
                'level': invitee.level,
                'children': invitee.get_invitation_tree(level + 1, max_depth)
            }
            result.append(invitee_data)
        return result

# 当创建新用户时自动创建用户资料
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class InvitationRecord(models.Model):
    """邀请记录模型"""
    inviter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_invitations', 
                              verbose_name='邀请人')
    invitee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_invitation', 
                              verbose_name='被邀请人')
    invite_code = models.CharField(max_length=12, verbose_name='使用的邀请码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='邀请时间')
    status = models.CharField(max_length=20, choices=[
        ('pending', '待接受'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
    ], default='pending', verbose_name='状态')
    
    class Meta:
        verbose_name = '邀请记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['inviter', 'invitee']
    
    def __str__(self):
        return f"{self.inviter.user.username} 邀请 {self.invitee.user.username}"


class ShippingAddress(models.Model):
    """用户收货地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses', verbose_name='用户')
    recipient_name = models.CharField(max_length=100, verbose_name='收件人姓名')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    province = models.CharField(max_length=50, verbose_name='省/直辖市')
    city = models.CharField(max_length=50, verbose_name='城市')
    district = models.CharField(max_length=50, verbose_name='区/县')
    address = models.CharField(max_length=200, verbose_name='详细地址')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='邮政编码')
    is_default = models.BooleanField(default=False, verbose_name='是否默认地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        ordering = ['-is_default', '-created_at']
        
    def __str__(self):
        return f"{self.recipient_name} - {self.province}{self.city}{self.district}{self.address}"
    
    def save(self, *args, **kwargs):
        # 如果设置为默认地址，将用户的其他地址设置为非默认
        if self.is_default:
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        # 如果用户没有其他地址，则将当前地址设为默认
        elif not ShippingAddress.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """获取完整地址"""
        return f"{self.province} {self.city} {self.district} {self.address}"
