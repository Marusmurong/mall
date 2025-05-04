from django.contrib import admin
from django.utils.html import format_html
from .models import Banner, HomeBlock, PageContent, SiteSettings

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
    list_display = ['title', 'block_type', 'sort_order', 'is_active', 'created_at']
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

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'slug', 'sort_order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('基本信息', {
                'fields': ('title', 'subtitle', 'slug', 'category')
            }),
            ('内容', {
                'fields': ('content', 'html_content')
            }),
            ('SEO设置', {
                'fields': ('meta_title', 'meta_description'),
                'classes': ('collapse',),
            }),
            ('显示设置', {
                'fields': ('sort_order', 'is_active', 'visible_in')
            }),
        ]
        return fieldsets

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'description', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['key', 'description']

# 添加admin标题设置
admin.site.site_header = "Cartitop管理后台"
admin.site.site_title = "Cartitop管理系统" 
admin.site.index_title = "网站管理"

# 修改应用名称显示
Banner._meta.verbose_name = '横幅广告'
Banner._meta.verbose_name_plural = '横幅广告'

HomeBlock._meta.verbose_name = '首页区块'
HomeBlock._meta.verbose_name_plural = '首页区块'

PageContent._meta.verbose_name = '页面内容'
PageContent._meta.verbose_name_plural = '页面内容'

SiteSettings._meta.verbose_name = '站点设置'
SiteSettings._meta.verbose_name_plural = '站点设置'

# 设置应用分组
from django.contrib.admin.apps import AdminConfig

# 注：应用分组在 apps.py 中通过 ContentConfig 类的 verbose_name 属性设置
