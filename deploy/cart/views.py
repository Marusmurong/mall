from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from goods.models import Goods
from .models import Cart, CartItem
import json
import uuid

def _get_cart(request):
    """获取或创建购物车"""
    if request.user.is_authenticated:
        # 登录用户 - 根据用户获取或创建购物车
        cart, created = Cart.objects.get_or_create(user=request.user)
        # 如果用户之前有会话购物车，则合并
        if 'cart_session_id' in request.session:
            session_id = request.session['cart_session_id']
            try:
                session_cart = Cart.objects.get(session_id=session_id)
                # 合并商品
                for item in session_cart.items.all():
                    # 检查是否已存在相同商品
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, 
                        product=item.product,
                        defaults={'quantity': 0}
                    )
                    # 增加商品数量
                    cart_item.quantity += item.quantity
                    cart_item.save()
                # 删除会话购物车
                session_cart.delete()
                # 删除会话ID
                del request.session['cart_session_id']
            except Cart.DoesNotExist:
                pass
    else:
        # 游客 - 根据会话ID获取或创建购物车
        if 'cart_session_id' not in request.session:
            request.session['cart_session_id'] = str(uuid.uuid4())
        
        session_id = request.session['cart_session_id']
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    
    return cart

def cart_detail(request):
    """显示购物车内容"""
    cart = _get_cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})

@require_POST
def add_to_cart(request):
    """添加商品到购物车"""
    cart = _get_cart(request)
    
    # 获取商品信息
    try:
        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Goods, id=product_id)
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': '无效的商品ID或数量'})
    
    # 检查商品库存
    if not product.is_new:
        return JsonResponse({'status': 'error', 'message': '该商品已售罄'})
    
    # 获取或创建购物车项目
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0}
    )
    
    # 更新数量
    cart_item.quantity += quantity
    cart_item.save()
    
    # 返回响应
    return JsonResponse({
        'status': 'success',
        'message': '成功加入购物车',
        'cart_count': cart.count
    })

@require_POST
def update_cart(request):
    """更新购物车商品数量"""
    cart = _get_cart(request)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': '无效的请求数据'})
    
    # 获取购物车项目
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '购物车项目不存在'})
    
    # 检查库存情况
    if not cart_item.product.is_new:
        return JsonResponse({'status': 'error', 'message': '该商品已售罄'})
    
    # 更新数量
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    # 返回更新后的购物车信息
    cart_data = {
        'status': 'success',
        'item_total': cart_item.total if quantity > 0 else 0,
        'cart_total': cart.total,
        'cart_count': cart.count
    }
    
    return JsonResponse(cart_data)

@require_POST
def remove_from_cart(request):
    """从购物车中移除商品"""
    cart = _get_cart(request)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        item_id = data.get('item_id')
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': '无效的请求数据'})
    
    # 获取并删除购物车项目
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '购物车项目不存在'})
    
    # 返回更新后的购物车信息
    return JsonResponse({
        'status': 'success',
        'message': '成功移除商品',
        'cart_total': cart.total,
        'cart_count': cart.count
    })
