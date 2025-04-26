from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.utils import get_current_site
from mall.settings import SITE_NAMES, DEFAULT_API_TOKEN
from django.conf import settings
import requests
import os
import json

@require_http_methods(["GET"])
def alokai_template_view(request):
    """渲染Alokai站点模板"""
    current_site = get_current_site()
    site_name = SITE_NAMES.get(current_site, 'Default Mall')
    
    # 从Alokai平台获取站点配置
    site_config = get_site_config(current_site)
    
    context = {
        'site_name': site_name,
        'site_config': site_config,
        'DEFAULT_API_TOKEN': DEFAULT_API_TOKEN
    }
    return render(request, 'site_templates/alokai/base.html', context)

@require_http_methods(["GET"])
def category_view(request, slug):
    """分类页面视图"""
    current_site = get_current_site()
    site_config = get_site_config(current_site)
    
    # 从API获取分类数据
    try:
        response = requests.get(
            f'{settings.API_BASE_URL}/categories/{slug}/',
            headers={'Authorization': f'Bearer {DEFAULT_API_TOKEN}'},
            timeout=5
        )
        if response.status_code == 200:
            category_data = response.json()
    except requests.RequestException as e:
        category_data = {}
        print(f"获取分类数据失败: {e}")
    
    context = {
        'site_config': site_config,
        'category': category_data.get('category', {}),
        'products': category_data.get('products', []),
        'sub_categories': category_data.get('sub_categories', []),
        'filters': category_data.get('filters', []),
        'sort_options': category_data.get('sort_options', []),
        'pagination': category_data.get('pagination', {})
    }
    return render(request, 'site_templates/alokai/category.html', context)

@require_http_methods(["GET"])
def product_view(request, id):
    """商品详情页面视图"""
    current_site = get_current_site()
    site_config = get_site_config(current_site)
    
    # 从API获取商品数据
    try:
        response = requests.get(
            f'{settings.API_BASE_URL}/products/{id}/',
            headers={'Authorization': f'Bearer {DEFAULT_API_TOKEN}'},
            timeout=5
        )
        if response.status_code == 200:
            product_data = response.json()
    except requests.RequestException as e:
        product_data = {}
        print(f"获取商品数据失败: {e}")
    
    context = {
        'site_config': site_config,
        'product': product_data.get('product', {}),
        'related_products': product_data.get('related_products', []),
        'recommendations': product_data.get('recommendations', [])
    }
    return render(request, 'site_templates/alokai/product.html', context)

@require_http_methods(["GET"])
def cart_view(request):
    """购物车页面视图"""
    current_site = get_current_site()
    site_config = get_site_config(current_site)
    
    # 从API获取购物车数据
    try:
        response = requests.get(
            f'{settings.API_BASE_URL}/cart/',
            headers={'Authorization': f'Bearer {DEFAULT_API_TOKEN}'},
            timeout=5
        )
        if response.status_code == 200:
            cart_data = response.json()
    except requests.RequestException as e:
        cart_data = {}
        print(f"获取购物车数据失败: {e}")
    
    context = {
        'site_config': site_config,
        'cart_items': cart_data.get('items', []),
        'cart_total': cart_data.get('total', 0),
        'cart_promotions': cart_data.get('promotions', [])
    }
    return render(request, 'site_templates/alokai/cart.html', context)

@require_http_methods(["GET"])
def wishlist_view(request):
    """心愿单页面视图"""
    current_site = get_current_site()
    site_config = get_site_config(current_site)
    
    # 从API获取心愿单数据
    try:
        response = requests.get(
            f'{settings.API_BASE_URL}/wishlist/',
            headers={'Authorization': f'Bearer {DEFAULT_API_TOKEN}'},
            timeout=5
        )
        if response.status_code == 200:
            wishlist_data = response.json()
    except requests.RequestException as e:
        wishlist_data = {}
        print(f"获取心愿单数据失败: {e}")
    
    context = {
        'site_config': site_config,
        'wishlist_items': wishlist_data.get('items', []),
        'wishlist_total': wishlist_data.get('total', 0),
        'recommendations': wishlist_data.get('recommendations', [])
    }
    return render(request, 'site_templates/alokai/wishlist.html', context)

def get_site_config(site_id):
    """从本地API获取站点配置"""
    try:
        response = requests.get(
            f'{settings.LOCAL_API_CONFIG["API_URL"]}/sites/{site_id}/config',
            headers={'Authorization': f'Bearer {DEFAULT_API_TOKEN}'},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"获取站点配置失败: {e}")
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

def site_editor_view(request, site_id=None):
    """站点编辑器视图"""
    current_site = get_current_site()
    
    # 获取站点配置
    site_config = get_site_config(current_site)
    
    # 获取站点区块配置
    blocks = get_site_blocks(current_site)
    
    context = {
        'site_config': site_config,
        'blocks': blocks,
        'site_id': site_id or current_site
    }
    return render(request, 'site_editor.html', context)

# API视图
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from api.utils import get_current_site
from mall.settings import SITE_NAMES
import json

@csrf_exempt
@require_http_methods(["GET"])
def get_site_config(request):
    """获取站点配置"""
    current_site = get_current_site()
    
    # 模拟站点配置数据
    site_config = {
        'name': 'Alokai 商城',
        'theme': 'default',
        'features': {
            'wishlist': True,
            'cart': True,
            'user_profile': True
        },
        'banners': [
            {
                'id': 1,
                'image': 'https://via.placeholder.com/1920x400',
                'title': '春季特惠'
            }
        ],
        'featured_products': [
            {
                'id': 1,
                'name': '商品1',
                'price': '¥199.00',
                'image': 'https://via.placeholder.com/300x300'
            },
            {
                'id': 2,
                'name': '商品2',
                'price': '¥299.00',
                'image': 'https://via.placeholder.com/300x300'
            }
        ]
    }
    
    return JsonResponse(site_config)

@csrf_exempt
@require_http_methods(["GET"])
def get_site_blocks(request, site_id):
    """获取站点区块配置"""
    # 在实际应用中，这些数据应该从数据库中获取
    # 这里我们返回一些示例数据
    
    # 获取一些分类数据
    categories = GoodsCategory.objects.filter(visible_in__contains=[site_id])[:4]
    category_data = []
    for category in categories:
        category_data.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug if hasattr(category, 'slug') else f'category-{category.id}',
            'image': category.image.url if hasattr(category, 'image') and category.image else None
        })
    
    # 获取一些商品数据
    products = Goods.objects.filter(visible_in__contains=[site_id])[:8]
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug if hasattr(product, 'slug') else f'product-{product.id}',
            'price': str(product.shop_price),
            'discount_price': str(product.market_price) if product.market_price < product.shop_price else None,
            'image': product.image.url if hasattr(product, 'image') and product.image else None
        })
    
    blocks = [
        {
            'type': 'hero-banner',
            'data': {
                'title': '欢迎来到我们的商城',
                'subtitle': '发现最新的产品和特惠',
                'buttonText': '立即购物',
                'buttonLink': '/products',
                'backgroundImage': '/static/img/hero-bg.jpg'
            }
        },
        {
            'type': 'featured-categories',
            'data': {
                'title': '热门分类',
                'categories': category_data
            }
        },
        {
            'type': 'product-showcase',
            'data': {
                'title': '热销商品',
                'products': product_data
            }
        },
        {
            'type': 'wishlist-section',
            'data': {
                'title': '创建您的心愿单',
                'description': '将您喜爱的商品添加到心愿单，随时查看并分享给朋友。',
                'buttonText': '查看心愿单',
                'buttonLink': '/wishlist'
            }
        }
    ]
    return JsonResponse(blocks, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def get_sites(request):
    """获取所有可用站点"""
    sites = []
    for site_id, site_name in SITE_NAMES.items():
        sites.append({
            'id': site_id,
            'name': site_name,
            'url': f'/?site={site_id}',
            'icon': site_id[0].upper(),
            'shortDescription': f'{site_name}商城，提供优质的{site_name}相关产品。'
        })
    
    return JsonResponse({'results': sites})

@csrf_exempt
@require_http_methods(["PUT"])
def update_site_config(request, site_id):
    """更新站点配置"""
    # 在实际应用中，这里应该将数据保存到数据库
    try:
        data = json.loads(request.body)
        # 这里应该有保存逻辑
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def update_site_blocks(request, site_id):
    """更新站点区块"""
    # 在实际应用中，这里应该将数据保存到数据库
    try:
        data = json.loads(request.body)
        # 这里应该有保存逻辑
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def api_gateway(request, path):
    """API网关，将请求转发到Vue.js应用"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def static_proxy(request, path):
    """静态资源代理，处理Vue.js应用的静态文件"""
    from django.conf import settings
    from django.http import FileResponse
    import os
    
    static_path = os.path.join(settings.BASE_DIR, 'frontend/dist', path)
    if os.path.exists(static_path):
        return FileResponse(open(static_path, 'rb'))
    return JsonResponse({"error": "File not found"}, status=404)

@csrf_exempt
@require_http_methods(["GET"])
def index(request):
    """Vue.js应用的入口页面"""
    return render(request, 'index.html')
