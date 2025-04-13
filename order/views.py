from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Order, OrderItem
from goods.models import Goods

@login_required
def order_list(request):
    """显示用户的订单列表"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order/order_list.html', {'orders': orders})

@login_required
def create_order(request):
    """创建新订单"""
    if request.method == 'POST':
        # 这里添加创建订单的逻辑
        return redirect('order:detail', order_id=1)  # 替换为实际的订单ID
    return render(request, 'order/create_order.html')

@login_required
def order_detail(request, order_id):
    """显示订单详情"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order/order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    """取消订单"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        order.status = 'cancelled'
        order.save()
        return redirect('order:detail', order_id=order.id)
    return render(request, 'order/cancel_order.html', {'order': order})
