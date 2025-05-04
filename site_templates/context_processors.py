from api.utils import get_current_site
from mall.settings import SITE_NAMES, DEFAULT_API_TOKEN

def site_config(request):
    """添加站点配置到模板上下文"""
    current_site = get_current_site()
    site_name = SITE_NAMES.get(current_site, 'Default Mall')
    
    # 使用本地固定配置，不再访问外部API
    site_config = {
        'theme': 'default',
        'features': {
            'wishlist': True,
            'cart': True,
            'user_profile': True
        }
    }
    
    return {
        'site_config': site_config,
        'site_name': site_name,
        'DEFAULT_API_TOKEN': DEFAULT_API_TOKEN
    }
