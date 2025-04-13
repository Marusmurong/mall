from django.contrib import admin
from django.utils.html import format_html
from .models import Banner, HomeBlock

# 注册管理界面

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'display_image', 'position', 'link', 'product', 'sort_order', 'is_active', 'created_at']
    list_filter = ['position', 'is_active']
    search_fields = ['title', 'link']
    list_editable = ['sort_order', 'is_active']
    autocomplete_fields = ['product']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'image', 'display_image', 'link', 'product', 'position')
        }),
        ('显示设置', {
            'fields': ('sort_order', 'is_active', 'visible_in', 'start_time', 'end_time')
        }),
    )
    readonly_fields = ['display_image', 'created_at', 'updated_at']
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{0}" width="100" height="auto" />', obj.image.url)
        return '-'
    display_image.short_description = '预览图片'

@admin.register(HomeBlock)
class HomeBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'block_type', 'sort_order', 'is_active', 'created_at']
    list_filter = ['block_type', 'is_active']
    search_fields = ['title', 'subtitle']
    list_editable = ['sort_order', 'is_active']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'subtitle', 'block_type', 'content', 'image', 'link')
        }),
        ('显示设置', {
            'fields': ('sort_order', 'is_active', 'visible_in')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
