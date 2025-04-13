from django.shortcuts import render, get_object_or_404
from .models import Goods, GoodsCategory, GoodsImage

def product_list(request, category_slug=None):
    """商品列表页面 - 使用新模板"""
    # 获取所有商品分类
    categories = GoodsCategory.objects.filter(is_active=True)
    all_categories = categories
    
    # 初始化category变量
    category = None
    
    # 处理URL传参的情况 - 从URL路径获取分类
    if category_slug:
        try:
            category = GoodsCategory.objects.get(name__iexact=category_slug)
            products = Goods.objects.filter(category=category, status='published')
        except GoodsCategory.DoesNotExist:
            products = Goods.objects.filter(status='published')
    # 处理GET参数的情况 - 从查询字符串获取分类
    else:
        category_param = request.GET.get('category', None)
        if category_param:
            # 尝试通过ID查找
            try:
                category_id = int(category_param)
                category = GoodsCategory.objects.get(id=category_id)
                products = Goods.objects.filter(category=category, status='published')
            except (ValueError, GoodsCategory.DoesNotExist):
                # 如果不是ID，尝试通过名称查找
                try:
                    category = GoodsCategory.objects.get(name__iexact=category_param)
                    products = Goods.objects.filter(category=category, status='published')
                except GoodsCategory.DoesNotExist:
                    # 如果也找不到，返回所有商品
                    products = Goods.objects.filter(status='published')
        else:
            # 没有分类参数，返回所有商品
            products = Goods.objects.filter(status='published')
    
    # 处理价格筛选
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # 处理排序
    sort = request.GET.get('sort')
    if sort == 'price-low':
        products = products.order_by('price')
    elif sort == 'price-high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    
    context = {
        'products': products,
        'categories': categories,
        'all_categories': all_categories,
        'category': category,
    }
    
    # 始终使用商品列表模板，除非是首页请求
    if request.path == '/':
        return render(request, 'shop/home.html', context)
    else:
        return render(request, 'shop/product_list.html', context)

def product_detail(request, product_id):
    """商品详情页面 - 使用新模板"""
    product = get_object_or_404(Goods, pk=product_id)
    
    # 获取商品所有图片
    product_images = product.images.all()
    
    # 获取相关商品（同类别的其他商品）
    related_products = Goods.objects.filter(
        category=product.category, 
        status='published'
    ).exclude(pk=product.pk)[:4]
    
    context = {
        'product': product,
        'product_images': product_images,
        'related_products': related_products
    }
    
    # 使用新模板
    return render(request, 'product/product_detail.html', context)

def home(request):
    """首页 - 使用新的模板"""
    # 获取推荐商品
    featured_products = Goods.objects.filter(is_recommended=True, status='published')[:8]
    
    # 获取所有活跃分类
    categories = GoodsCategory.objects.filter(is_active=True, parent__isnull=True)
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    
    return render(request, 'shop/home.html', context)
