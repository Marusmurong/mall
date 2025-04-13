from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from goods.models import GoodsCategory, Goods
from api.utils import get_current_site
from mall.settings import SITE_NAMES

def alokai_template_view(request):
    """渲染Alokai站点模板"""
    current_site = get_current_site()
    site_name = SITE_NAMES.get(current_site, 'Default Mall')
    
    context = {
        'current_site_id': current_site,
        'site_name': site_name,
    }
    return render(request, 'alokai_site_template.html', context)

@login_required
def site_editor_view(request, site_id=None):
    """站点编辑器视图"""
    # 检查用户是否有权限编辑站点
    if not request.user.is_staff and not request.user.is_superuser:
        return render(request, '403.html', {'message': '您没有权限访问站点编辑器'})
    
    # 如果没有指定site_id，使用当前站点
    if not site_id:
        site_id = get_current_site()
    
    site_name = SITE_NAMES.get(site_id, 'Default Mall')
    
    context = {
        'site_id': site_id,
        'site_name': site_name,
    }
    return render(request, 'site_editor.html', context)

# API视图
@require_http_methods(["GET"])
def get_site_config(request, site_id):
    """获取站点配置"""
    # 在实际应用中，这些数据应该从数据库中获取
    config = {
        'name': SITE_NAMES.get(site_id, 'Default Mall'),
        'logo': '/static/img/logo.png',
        'announcement': '欢迎光临我们的商城！全场满300减50！',
        'description': '我们致力于为您提供最优质的产品和服务。',
        'socialLinks': [
            {'name': 'facebook', 'url': 'https://facebook.com'},
            {'name': 'instagram', 'url': 'https://instagram.com'},
            {'name': 'twitter', 'url': 'https://twitter.com'},
            {'name': 'youtube', 'url': 'https://youtube.com'}
        ]
    }
    return JsonResponse(config)

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
