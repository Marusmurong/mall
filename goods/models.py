from django.db import models
from django.conf import settings

# 导入站点中间件函数
from mall.middleware.site_middleware import get_current_site

# Create your models here.

class GoodsCategory(models.Model):
    """商品分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父级分类', related_name='children')
    level = models.PositiveIntegerField(default=1, verbose_name='分类级别')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    description = models.TextField(blank=True, verbose_name='分类描述')

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Goods(models.Model):
    """商品"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('sold_out', '已售罄'),
        ('off_shelf', '已下架'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='商品名称')
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='商品分类', related_name='goods')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    stock = models.PositiveIntegerField(default=0, verbose_name='库存')
    sales = models.PositiveIntegerField(default=0, verbose_name='销量')
    image = models.ImageField(upload_to='goods/images/', null=True, blank=True, verbose_name='主图')
    description = models.TextField(blank=True, verbose_name='商品描述')
    goods_desc = models.TextField(blank=True, verbose_name='商品详细描述')
    source_url = models.URLField(max_length=500, blank=True, verbose_name='商品来源URL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')
    is_new = models.BooleanField(default=True, verbose_name='是否新品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    visible_in = models.JSONField(default=list, blank=True, verbose_name='可见站点')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name
        
    def is_visible_in_current_site(self):
        """判断商品在当前站点是否可见"""
        current_site = get_current_site()
        # 如果visible_in为空列表，则在所有站点可见
        if not self.visible_in:
            return True
        # 否则只在指定站点可见
        return current_site in self.visible_in
        
    def save(self, *args, **kwargs):
        # 如果没有设置主图，但有商品图片，则将第一张图片设为主图
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new or not self.image:
            # 检查是否有商品图片
            main_image = self.images.filter(is_main=True).first()
            if main_image and not self.image:
                self.image = main_image.image
                super().save(update_fields=['image'])


class GoodsImage(models.Model):
    """商品图片"""
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image = models.ImageField(upload_to='goods/images/', verbose_name='图片')
    is_main = models.BooleanField(default=False, verbose_name='是否主图')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.goods.name} - 图片{self.sort_order}"
