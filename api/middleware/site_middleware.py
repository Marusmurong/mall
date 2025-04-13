from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_current_site(request=None):
    """
    获取当前站点标识
    如果提供了request，则从request中获取
    否则返回默认站点
    """
    if request and hasattr(request, 'site'):
        return request.site
    return 'default'

class SiteMiddleware:
    """
    站点中间件
    用于检测当前请求所属的站点
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.site_mapping = getattr(settings, 'SITE_MAPPING', {})
        self.site_names = getattr(settings, 'SITE_NAMES', {})
        
    def __call__(self, request):
        # 默认站点
        request.site = 'default'
        request.site_name = self.site_names.get('default', '默认站点')
        
        # 从请求参数中获取站点
        site_param = request.GET.get('site')
        if site_param and site_param in self.site_names:
            request.site = site_param
            request.site_name = self.site_names.get(site_param)
            return self.get_response(request)
            
        # 从HTTP头中获取站点
        site_header = request.headers.get('X-Site')
        if site_header and site_header in self.site_names:
            request.site = site_header
            request.site_name = self.site_names.get(site_header)
            return self.get_response(request)
            
        # 从域名中获取站点
        host = request.get_host()
        if host in self.site_mapping:
            request.site = self.site_mapping[host]
            request.site_name = self.site_names.get(request.site, request.site)
            
        return self.get_response(request)
