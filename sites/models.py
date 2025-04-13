from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class Site(models.Model):
    """站点模型，用于管理多个分站"""
    name = models.CharField(_('站点名称'), max_length=100)
    code = models.SlugField(
        _('站点代码'), 
        max_length=50, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-z0-9_-]+$',
            message='站点代码只能包含小写字母、数字、下划线和连字符'
        )],
        help_text=_('唯一的站点标识符，用于API请求和URL')
    )
    domain = models.CharField(
        _('域名'), 
        max_length=100, 
        blank=True,
        help_text=_('站点的主域名，例如：example.com')
    )
    is_active = models.BooleanField(_('是否激活'), default=True)
    description = models.TextField(_('描述'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    # 站点配置
    logo = models.ImageField(_('站点Logo'), upload_to='sites/logos/', blank=True, null=True)
    favicon = models.ImageField(_('站点图标'), upload_to='sites/favicons/', blank=True, null=True)
    primary_color = models.CharField(_('主色调'), max_length=20, blank=True, default='#3b82f6')
    secondary_color = models.CharField(_('次色调'), max_length=20, blank=True, default='#10b981')
    
    # API配置
    api_url = models.URLField(
        _('API URL'), 
        blank=True,
        help_text=_('站点API的基础URL，如果为空则使用默认URL')
    )
    api_key = models.CharField(_('API密钥'), max_length=100, blank=True)
    
    # 前端配置
    frontend_url = models.URLField(
        _('前端URL'), 
        blank=True,
        help_text=_('前端应用的URL，如果为空则使用域名')
    )
    frontend_port = models.PositiveIntegerField(
        _('前端端口'), 
        default=3000,
        help_text=_('前端应用运行的端口')
    )
    
    class Meta:
        verbose_name = _('站点')
        verbose_name_plural = _('站点管理')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SiteTheme(models.Model):
    """站点主题配置"""
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='theme')
    
    # 颜色配置
    header_bg_color = models.CharField(_('头部背景色'), max_length=20, blank=True, default='#ffffff')
    footer_bg_color = models.CharField(_('底部背景色'), max_length=20, blank=True, default='#1f2937')
    button_color = models.CharField(_('按钮颜色'), max_length=20, blank=True, default='#3b82f6')
    link_color = models.CharField(_('链接颜色'), max_length=20, blank=True, default='#3b82f6')
    
    # 字体配置
    heading_font = models.CharField(_('标题字体'), max_length=50, blank=True, default='sans-serif')
    body_font = models.CharField(_('正文字体'), max_length=50, blank=True, default='sans-serif')
    
    # 布局配置
    layout_type = models.CharField(
        _('布局类型'),
        max_length=20,
        choices=[
            ('default', _('默认')),
            ('compact', _('紧凑')),
            ('wide', _('宽屏')),
        ],
        default='default'
    )
    
    # 自定义CSS
    custom_css = models.TextField(_('自定义CSS'), blank=True)
    
    class Meta:
        verbose_name = _('站点主题')
        verbose_name_plural = _('站点主题')
    
    def __str__(self):
        return f"{self.site.name}的主题配置"


class SiteSlide(models.Model):
    """站点首页幻灯片"""
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='slides')
    title = models.CharField(_('标题'), max_length=200)
    subtitle = models.CharField(_('副标题'), max_length=200, blank=True)
    image = models.ImageField(_('图片'), upload_to='sites/slides/')
    button_text = models.CharField(_('按钮文字'), max_length=50, blank=True)
    button_link = models.CharField(_('按钮链接'), max_length=200, blank=True)
    background_color = models.CharField(_('背景颜色'), max_length=20, blank=True, default='bg-gradient-to-r from-primary-700 to-primary-900')
    order = models.PositiveIntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否激活'), default=True)
    
    class Meta:
        verbose_name = _('首页幻灯片')
        verbose_name_plural = _('首页幻灯片')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.site.name} - {self.title}"


class SiteConfig(models.Model):
    """站点其他配置"""
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='config')
    
    # 联系信息
    contact_email = models.EmailField(_('联系邮箱'), blank=True)
    contact_phone = models.CharField(_('联系电话'), max_length=20, blank=True)
    contact_address = models.TextField(_('联系地址'), blank=True)
    
    # 社交媒体
    facebook_url = models.URLField(_('Facebook链接'), blank=True)
    twitter_url = models.URLField(_('Twitter链接'), blank=True)
    instagram_url = models.URLField(_('Instagram链接'), blank=True)
    youtube_url = models.URLField(_('YouTube链接'), blank=True)
    
    # SEO配置
    meta_title = models.CharField(_('Meta标题'), max_length=100, blank=True)
    meta_description = models.TextField(_('Meta描述'), blank=True)
    meta_keywords = models.CharField(_('Meta关键词'), max_length=200, blank=True)
    
    # 其他配置
    google_analytics_id = models.CharField(_('Google Analytics ID'), max_length=50, blank=True)
    facebook_pixel_id = models.CharField(_('Facebook Pixel ID'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('站点配置')
        verbose_name_plural = _('站点配置')
    
    def __str__(self):
        return f"{self.site.name}的配置"
