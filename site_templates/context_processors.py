from api.utils import get_current_site
from mall.settings import SITE_NAMES, DEFAULT_API_TOKEN, LOCAL_API_CONFIG
from django.conf import settings

def site_config(request):
    """添加站点配置到模板上下文"""
    current_site = get_current_site()
    site_name = SITE_NAMES.get(current_site, 'Default Mall')
    
    # 使用本地配置代替从Alokai平台获取站点配置
    try:
        import requests
        response = requests.get(
            f'{LOCAL_API_CONFIG["API_URL"]}/sites/{current_site}/config',
            headers={'Authorization': f'Bearer {DEFAULT_API_TOKEN}'},
            timeout=5
        )
        if response.status_code == 200:
            site_config = response.json()
        else:
            # 如果API调用失败，使用默认配置
            site_config = get_default_site_config(current_site)
    except Exception as e:
        print(f"获取站点配置失败: {e}")
        site_config = get_default_site_config(current_site)
    
    return {
        'site_config': site_config,
        'site_name': site_name,
        'DEFAULT_API_TOKEN': DEFAULT_API_TOKEN,
        'LOCAL_API_CONFIG': LOCAL_API_CONFIG
    }

def get_default_site_config(site_id):
    """获取默认站点配置"""
    return {
        'id': site_id,
        'name': SITE_NAMES.get(site_id, 'Default Mall'),
        'theme': 'default',
        'features': {
            'wishlist': True,
            'cart': True,
            'user_profile': True
        }
    }
