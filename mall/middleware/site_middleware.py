from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import threading

# 全局线程本地存储，用于在请求处理过程中存储当前站点信息
_thread_local = threading.local()

class SiteMiddleware(MiddlewareMixin):
    """
    中间件用于检测当前请求所属的站点
    基于请求的域名或者其他信息来判断当前站点
    """
    
    def process_request(self, request):
        """
        处理每个请求，确定当前站点并存储到线程本地变量
        """
        # 默认站点为 'default'
        current_site = 'default'
        
        # 通过域名判断当前站点
        host = request.get_host()
        
        # 示例站点映射，可以根据需要进行配置
        # 也可以将此配置移动到 settings.py 中
        site_mapping = getattr(settings, 'SITE_MAPPING', {
            'us.example.com': 'us',
            'asia.example.com': 'asia',
            'localhost:8000': 'default',  # 本地开发环境
            '127.0.0.1:8000': 'default',  # 本地开发环境
        })
        
        # 根据域名确定站点
        if host in site_mapping:
            current_site = site_mapping[host]
        else:
            # 可以添加更多的判断逻辑，例如基于请求路径、用户地理位置等
            # 这里使用默认站点
            pass
        
        # 将当前站点存储到线程本地变量
        _thread_local.current_site = current_site
        
        # 将当前站点添加到请求对象，方便在视图中使用
        request.current_site = current_site
        
        # 中间件不需要返回任何响应，继续处理请求


def get_current_site():
    """
    获取当前请求的站点
    可以在模型、视图、模板等地方使用
    """
    return getattr(_thread_local, 'current_site', 'default')
