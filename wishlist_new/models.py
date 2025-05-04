import uuid
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from goods.models import Goods

User = get_user_model()

class Wishlist(models.Model):
    """心愿单"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_('名称'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists_new', verbose_name='用户')
    description = models.TextField(blank=True, verbose_name=_('描述'))
    is_public = models.BooleanField(default=True, verbose_name=_('是否公开'))
    share_code = models.CharField(max_length=20, unique=True, blank=True, verbose_name=_('分享码'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        app_label = 'wishlist_new'
        verbose_name = '心愿单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.user.username}的心愿单'
    
    def save(self, *args, **kwargs):
        if not self.share_code:
            self.share_code = self.generate_share_code()
        super().save(*args, **kwargs)
    
    def generate_share_code(self):
        """生成分享码"""
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # 检查是否已存在
        while Wishlist.objects.filter(share_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return code
    
    def get_absolute_url(self):
        return reverse('wishlist_detail', args=[str(self.id)])
    
    def get_share_url(self):
        return reverse('wishlist_share', args=[self.share_code])
        
    def get_view_count(self):
        """获取心愿单浏览次数"""
        return self.views.count()


class WishlistItem(models.Model):
    """心愿单物品"""
    PRIORITY_CHOICES = (
        ('low', _('低')),
        ('medium', _('中')),
        ('high', _('高')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items', verbose_name='心愿单')
    # 临时将product字段设为可选，便于迁移
    product = models.ForeignKey(Goods, on_delete=models.CASCADE, null=True, blank=True, verbose_name='商品')
    title = models.CharField(max_length=100, verbose_name=_('标题'))
    description = models.TextField(blank=True, verbose_name=_('描述'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('价格'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('货币'))
    image = models.ImageField(upload_to='wishlist_items/', blank=True, null=True, verbose_name=_('图片'))
    url = models.URLField(blank=True, verbose_name=_('链接'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('优先级'))
    
    # 购买相关字段
    purchased = models.BooleanField(default=False, verbose_name=_('已被购买'))
    purchased_at = models.DateTimeField(null=True, blank=True, verbose_name=_('购买时间'))
    purchased_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='purchased_items_new', verbose_name=_('购买者'))
    
    # 支付相关字段
    current_payment = models.ForeignKey('payment.Payment', null=True, blank=True, on_delete=models.SET_NULL, related_name='current_item_new', verbose_name=_('当前支付'))
    payment_status = models.CharField(max_length=20, blank=True, verbose_name=_('支付状态'))
    payment_completed = models.BooleanField(default=False, verbose_name=_('支付已完成'))
    
    # 暂时移除auto_now_add并设置默认值以便迁移
    added_at = models.DateTimeField(default=timezone.now, verbose_name='添加时间')
    
    class Meta:
        app_label = 'wishlist_new'
        verbose_name = '心愿单商品'
        verbose_name_plural = verbose_name
        ordering = ['-added_at', 'priority']
        # 移除unique_together约束，允许在同一心愿单中添加多个相同商品
        
    def __str__(self):
        product_name = self.product.name if self.product else '未指定商品'
        return f'{self.wishlist.user.username}的心愿单 - {product_name}'
    
    def formatted_price(self):
        return f"{self.price} {self.currency}"
    
    def get_absolute_url(self):
        return reverse('wishlist_detail', args=[str(self.wishlist.id)])


class WishlistView(models.Model):
    """心愿单浏览记录"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='views', verbose_name='心愿单')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='用户')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='浏览时间')
    
    class Meta:
        app_label = 'wishlist_new'
        verbose_name = '心愿单浏览记录'
        verbose_name_plural = verbose_name
        ordering = ['-viewed_at']
        
    def __str__(self):
        return f'{self.wishlist} - {self.viewed_at}'
