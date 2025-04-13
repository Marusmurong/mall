from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django import forms
from django.db import models
from .models import GoodsCategory, Goods, GoodsImage

# Register your models here.

@admin.register(GoodsCategory)
class GoodsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'level', 'is_active', 'sort_order', 'created_at']
    list_filter = ['level', 'is_active']
    search_fields = ['name']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'parent', 'level', 'description')
        }),
        ('显示设置', {
            'fields': ('is_active', 'sort_order')
        }),
    )


class GoodsImageInline(admin.TabularInline):
    model = GoodsImage
    extra = 1
    fields = ['image', 'display_image', 'is_main', 'sort_order']
    readonly_fields = ['display_image']
    
    def display_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="100" height="auto" style="max-height: 100px" />', obj.image.url)
        return '-'
    display_image.short_description = '图片预览'
    

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'original_price', 'stock', 'sales', 
                   'display_image', 'status', 'is_recommended', 'is_hot', 'is_new', 'created_at']
    list_filter = ['category', 'status', 'is_recommended', 'is_hot', 'is_new']
    
    # 自定义方法，用于过滤站点可见性
    def get_queryset(self, request):
        """
        如果不是超级用户，则只显示在当前站点可见的商品
        注意：此处用于演示，实际中可能需要更复杂的权限控制
        """
        queryset = super().get_queryset(request)
        
        # 超级用户可以看到所有商品
        if request.user.is_superuser:
            return queryset
            
        # 非超级用户只能看到对应站点可见的商品
        from mall.middleware.site_middleware import get_current_site
        current_site = get_current_site()
        
        # JSONField查询：visible_in为空或包含当前站点
        return queryset.filter(
            models.Q(visible_in__contains=current_site) | 
            models.Q(visible_in=[]) | 
            models.Q(visible_in__isnull=True)
        )
    search_fields = ['name', 'description', 'goods_desc']
    list_editable = ['price', 'stock', 'status', 'is_recommended', 'is_hot', 'is_new']
    readonly_fields = ['sales', 'created_at', 'updated_at']
    inlines = [GoodsImageInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'image', 'description')
        }),
        ('详细信息', {
            'fields': ('goods_desc',)
        }),
        ('价格与库存', {
            'fields': ('price', 'original_price', 'stock', 'sales')
        }),
        ('商品状态', {
            'fields': ('status', 'is_recommended', 'is_hot', 'is_new')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
        ('内部信息', {
            'fields': ('source_url',),
            'classes': ('collapse',),
        }),
        ('站点设置', {
            'fields': ('visible_in',),
            'description': '选择商品在哪些站点可见，不选择则在所有站点可见',
        }),
    )
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    display_image.short_description = '商品图片'
    
