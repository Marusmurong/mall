from django.contrib import admin
from django.utils.html import format_html
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
    )
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    display_image.short_description = '商品图片'
    
