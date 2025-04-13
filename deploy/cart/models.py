from django.db import models
from django.contrib.auth.models import User
from goods.models import GoodsCategory, Goods

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"购物车 - {self.user.username}"
        return f"购物车 - {self.session_id}"
    
    @property
    def total(self):
        """计算购物车总金额"""
        return sum(item.total for item in self.items.all())
    
    @property
    def count(self):
        """计算购物车商品总数"""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_price(self):
        """计算购物车总金额（为了兼容模板）"""
        return self.total
    
    class Meta:
        verbose_name = "购物车"
        verbose_name_plural = "购物车"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Goods, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    @property
    def total(self):
        """计算单项总金额"""
        return self.product.shop_price * self.quantity
    
    def get_cost(self):
        """计算单项总金额（为了兼容模板）"""
        return self.total
    
    class Meta:
        verbose_name = "购物车项目"
        verbose_name_plural = "购物车项目"
        unique_together = ('cart', 'product')
