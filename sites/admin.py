from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Site, SiteTheme, SiteSlide, SiteConfig


class SiteThemeInline(admin.StackedInline):
    model = SiteTheme
    can_delete = False
    verbose_name = _('站点主题')
    verbose_name_plural = _('站点主题')


class SiteConfigInline(admin.StackedInline):
    model = SiteConfig
    can_delete = False
    verbose_name = _('站点配置')
    verbose_name_plural = _('站点配置')


class SiteSlideInline(admin.TabularInline):
    model = SiteSlide
    extra = 1
    verbose_name = _('首页幻灯片')
    verbose_name_plural = _('首页幻灯片')


@admin.action(description=_('复制选中站点'))
def duplicate_site(modeladmin, request, queryset):
    for site in queryset:
        # 复制站点
        site.pk = None
        site.name = f"{site.name} (复制)"
        site.code = f"{site.code}_copy"
        site.domain = ""
        site.save()


class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'domain', 'is_active', 'frontend_port', 'created_at', 'view_site_link']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'domain']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': ['name', 'code', 'domain', 'is_active', 'description']
        }),
        (_('基本配置'), {
            'fields': ['logo', 'favicon', 'primary_color', 'secondary_color']
        }),
        (_('API配置'), {
            'fields': ['api_url', 'api_key']
        }),
        (_('前端配置'), {
            'fields': ['frontend_url', 'frontend_port']
        }),
        (_('时间信息'), {
            'fields': ['created_at', 'updated_at']
        }),
    ]
    inlines = [SiteThemeInline, SiteConfigInline, SiteSlideInline]
    actions = [duplicate_site]
    
    def view_site_link(self, obj):
        if obj.frontend_url:
            url = obj.frontend_url
        elif obj.domain:
            url = f"http://{obj.domain}"
        else:
            url = f"http://localhost:{obj.frontend_port}"
        
        return format_html('<a href="{}" target="_blank">{}</a>', url, _('查看站点'))
    
    view_site_link.short_description = _('站点链接')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # 确保每个站点都有主题和配置
        if not hasattr(obj, 'theme'):
            SiteTheme.objects.create(site=obj)
        
        if not hasattr(obj, 'config'):
            SiteConfig.objects.create(site=obj)


@admin.register(SiteSlide)
class SiteSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'order', 'is_active']
    list_filter = ['site', 'is_active']
    search_fields = ['title', 'subtitle']
    list_editable = ['order', 'is_active']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('site')


# 注册模型
admin.site.register(Site, SiteAdmin)
