from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class SiteAPIMiddleware(MiddlewareMixin):
    """
    API站点检测中间件
    用于检测API请求所属站点，支持通过查询参数方式指定站点
    """
    def process_request(self, request):
        # 检查URL查询参数中是否指定了站点
        site_code = request.GET.get('site', None)
        
        # 如果没有通过查询参数指定站点，则使用域名检测
        if not site_code:
            host = request.get_host()
            site_mapping = getattr(settings, 'SITE_MAPPING', {})
            
            if host in site_mapping:
                site_code = site_mapping[host]
            else:
                # 默认站点
                site_code = 'default'
        
        # 将站点代码存入请求对象，供后续处理使用
        request.site_code = site_code
        return None
