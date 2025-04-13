from api.utils import get_current_site
from mall.settings import SITE_NAMES, DEFAULT_API_TOKEN

def site_config(request):
    """添加站点配置到模板上下文"""
    current_site = get_current_site()
    site_name = SITE_NAMES.get(current_site, 'Default Mall')
    
    # 从Alokai平台获取站点配置
    try:
        import requests
        response = requests.get(
            f'https://platform.alokai.com/api/v1/sites/{current_site}/config',
            headers={'Authorization': f'Bearer {DEFAULT_API_TOKEN}'},
            timeout=5
        )
        if response.status_code == 200:
            site_config = response.json()
        else:
            site_config = {
                'theme': 'default',
                'features': {
                    'wishlist': True,
                    'cart': True,
                    'user_profile': True
                }
            }
    except Exception as e:
        print(f"获取站点配置失败: {e}")
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
