from django.db import models
from django.utils.translation import gettext_lazy as _
from goods.models import Goods

# 创建内容管理模型

class Banner(models.Model):
    """首页轮播图"""
    POSITION_CHOICES = [
        ('home_top', '首页顶部'),
        ('home_middle', '首页中部'),
        ('category', '分类页面'),
        ('product', '商品详情页'),
    ]
    
    title = models.CharField(max_length=100, verbose_name='标题')
    image = models.ImageField(upload_to='banners/', verbose_name='轮播图片')
    link = models.CharField(max_length=255, blank=True, verbose_name='链接地址')
    product = models.ForeignKey(Goods, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='关联商品')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='home_top', verbose_name='显示位置')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    visible_in = models.JSONField(default=list, blank=True, verbose_name='可见站点')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']
    
    def __str__(self):
        return self.title

class HomeBlock(models.Model):
    """首页内容区块"""
    BLOCK_TYPE_CHOICES = [
        ('product_list', '商品列表'),
        ('image_text', '图文组合'),
        ('brand_list', '品牌列表'),
        ('category_icons', '分类图标'),
        ('coupon_list', '优惠券列表'),
    ]
    
    title = models.CharField(max_length=100, verbose_name='区块标题')
    subtitle = models.CharField(max_length=200, blank=True, verbose_name='副标题')
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES, verbose_name='区块类型')
    content = models.JSONField(default=dict, blank=True, verbose_name='区块内容')
    image = models.ImageField(upload_to='blocks/', null=True, blank=True, verbose_name='区块图片')
    link = models.CharField(max_length=255, blank=True, verbose_name='链接地址')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    visible_in = models.JSONField(default=list, blank=True, verbose_name='可见站点')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '首页区块'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']
    
    def __str__(self):
        return self.title
