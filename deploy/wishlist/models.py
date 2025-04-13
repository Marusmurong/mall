from django.db import models
from django.contrib.auth.models import User
from goods.models import Goods
import uuid
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db import connection

class Wishlist(models.Model):
    """心愿单模型"""
    name = models.CharField(max_length=100, verbose_name='心愿单名称')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists', verbose_name='用户')
    share_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='分享码')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    view_count = models.PositiveIntegerField(default=0, verbose_name='访问量')
    last_viewed_at = models.DateTimeField(null=True, blank=True, verbose_name='最后访问时间')

    class Meta:
        verbose_name = '心愿单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_share_url(self):
        return f"/wishlist/share/{self.share_code}/"

    def get_total_price(self):
        """获取心愿单总价"""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT SUM(g.price * wi.quantity) 
                FROM wishlist_wishlistitem wi
                JOIN goods_goods g ON wi.product_id = g.id
                WHERE wi.wishlist_id = %s
                """, 
                [self.id]
            )
            result = cursor.fetchone()[0]
            return result or 0


class WishlistItem(models.Model):
    """心愿单物品"""
    PRIORITY_CHOICES = (
        ('low', _('低')),
        ('medium', _('中')),
        ('high', _('高')),
    )
    
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, verbose_name=_('心愿单'))
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
    purchased_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='purchased_items', verbose_name=_('购买者'))
    
    # 支付相关字段
    current_payment = models.ForeignKey('payment.Payment', null=True, blank=True, on_delete=models.SET_NULL, related_name='current_item', verbose_name=_('当前支付'))
    payment_status = models.CharField(max_length=20, blank=True, verbose_name=_('支付状态'))
    payment_completed = models.BooleanField(default=False, verbose_name=_('支付已完成'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    def __str__(self):
        return self.title
    
    def formatted_price(self):
        return f"{self.price} {self.currency}"
    
    def get_absolute_url(self):
        return reverse('wishlist_detail', args=[str(self.wishlist.id)])
