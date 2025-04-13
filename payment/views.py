from django.shortcuts import render
import json
import logging
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings

from wishlist_new.models import WishlistItem
from .models import Payment, PaymentMethod
from .processors import get_payment_processor

logger = logging.getLogger(__name__)


def payment_method_list(request, wishlist_item_id):
    """选择支付方式页面"""
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    
    # 检查心愿单物品是否已购买
    if wishlist_item.purchased:
        messages.warning(request, _('该心愿单物品已被购买'))
        return redirect('wishlist_detail', pk=wishlist_item.wishlist.id)
    
    # 获取可用的支付方式
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # 检查是否是匿名支付
    is_anonymous = not request.user.is_authenticated
    
    context = {
        'wishlist_item': wishlist_item,
        'payment_methods': payment_methods,
        'is_anonymous': is_anonymous,
    }
    return render(request, 'payment/payment_method_list.html', context)


def create_payment(request, wishlist_item_id):
    """创建支付记录"""
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    
    # 检查心愿单物品是否已购买
    if wishlist_item.purchased:
        messages.warning(request, _('该心愿单物品已被购买'))
        return redirect('wishlist_detail', pk=wishlist_item.wishlist.id)
    
    if request.method != 'POST':
        return redirect('payment_method_list', wishlist_item_id=wishlist_item_id)
    
    # 获取选择的支付方式
    payment_method_code = request.POST.get('payment_method')
    if not payment_method_code:
        messages.error(request, _('请选择支付方式'))
        return redirect('payment_method_list', wishlist_item_id=wishlist_item_id)
    
    # 获取支付处理器
    processor = get_payment_processor(payment_method_code)
    if not processor:
        messages.error(request, _('支付方式不可用'))
        return redirect('payment_method_list', wishlist_item_id=wishlist_item_id)
    
    # 检查是否是匿名支付
    is_anonymous = request.POST.get('is_anonymous') == 'on' or not request.user.is_authenticated
    payer = None if is_anonymous else request.user
    
    # 收集支付相关信息
    payer_email = request.POST.get('payer_email', '')
    payer_name = request.POST.get('payer_name', '')
    
    # 设置回调URL
    return_url = request.build_absolute_uri(
        reverse('payment_success', kwargs={'wishlist_item_id': wishlist_item_id})
    )
    cancel_url = request.build_absolute_uri(
        reverse('payment_cancel', kwargs={'wishlist_item_id': wishlist_item_id})
    )
    
    # 根据支付方式获取额外参数
    extra_params = {}
    if processor.payment_method.payment_type == 'usdt':
        extra_params['network'] = request.POST.get('network', 'trc20')
    
    # 创建支付记录
    payment = processor.create_payment(
        wishlist_item=wishlist_item,
        amount=Decimal(str(wishlist_item.price)),
        payer=payer,
        is_anonymous=is_anonymous,
        payer_email=payer_email,
        payer_name=payer_name,
        return_url=return_url,
        cancel_url=cancel_url,
        **extra_params
    )
    
    # 根据支付方式重定向到对应的处理页面
    if processor.payment_method.payment_type == 'usdt':
        return redirect('usdt_payment_detail', payment_id=payment.id)
    elif processor.payment_method.payment_type == 'paypal':
        # 重定向到PayPal支付页面
        checkout_url = payment.payment_data.get('checkout_url', '')
        if checkout_url:
            if checkout_url.startswith('/'):
                return redirect(checkout_url)
            else:
                return redirect(checkout_url)
        else:
            messages.error(request, _('创建PayPal支付失败'))
            return redirect('payment_method_list', wishlist_item_id=wishlist_item_id)
    elif processor.payment_method.payment_type == 'credit_card':
        # 重定向到信用卡支付页面
        return redirect('credit_card_checkout', payment_id=payment.id)
    else:
        messages.error(request, _('不支持的支付方式'))
        return redirect('payment_method_list', wishlist_item_id=wishlist_item_id)


def usdt_payment_detail(request, payment_id):
    """USDT支付详情页面"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # 检查支付状态
    if payment.status == 'completed':
        messages.success(request, _('支付已完成'))
        return redirect('payment_success', wishlist_item_id=payment.wishlist_item.id)
    
    # 获取USDT支付详情
    try:
        usdt_details = payment.usdt_details
    except:
        messages.error(request, _('支付信息不完整'))
        return redirect('payment_method_list', wishlist_item_id=payment.wishlist_item.id)
    
    # 处理交易哈希提交
    if request.method == 'POST':
        transaction_hash = request.POST.get('transaction_hash', '')
        sender_address = request.POST.get('sender_address', '')
        
        if not transaction_hash:
            messages.error(request, _('请提供交易哈希'))
            return redirect('usdt_payment_detail', payment_id=payment_id)
        
        # 获取支付处理器
        processor = get_payment_processor(payment.payment_method.code)
        if not processor:
            messages.error(request, _('支付方式不可用'))
            return redirect('payment_method_list', wishlist_item_id=payment.wishlist_item.id)
        
        # 处理支付
        result = processor.process_payment(
            payment=payment,
            transaction_hash=transaction_hash,
            sender_address=sender_address
        )
        
        if result.get('success'):
            messages.success(request, _(result.get('message')))
            return redirect('payment_status', payment_id=payment_id)
        else:
            messages.error(request, _(result.get('message')))
    
    context = {
        'payment': payment,
        'usdt_details': usdt_details,
        'wishlist_item': payment.wishlist_item,
    }
    return render(request, 'payment/usdt_payment_detail.html', context)


def paypal_checkout(request, payment_id):
    """PayPal结账回调处理"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # 获取PayPal回调参数
    paypal_order_id = request.GET.get('order_id', '')
    paypal_payer_id = request.GET.get('PayerID', '')
    
    # 如果没有payer_id，可能是初次加载页面或支付失败
    if not paypal_payer_id:
        return render(request, 'payment/paypal_checkout.html', {
            'payment': payment,
            'wishlist_item': payment.wishlist_item,
        })
    
    # 获取支付处理器
    processor = get_payment_processor(payment.payment_method.code)
    if not processor:
        messages.error(request, _('支付方式不可用'))
        return redirect('payment_method_list', wishlist_item_id=payment.wishlist_item.id)
    
    # 处理支付
    result = processor.process_payment(
        payment=payment,
        paypal_payer_id=paypal_payer_id
    )
    
    if result.get('success'):
        messages.success(request, _(result.get('message')))
        return redirect('payment_success', wishlist_item_id=payment.wishlist_item.id)
    else:
        messages.error(request, _(result.get('message')))
        return redirect('payment_status', payment_id=payment_id)


def credit_card_checkout(request, payment_id):
    """信用卡结账页面"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # 检查支付状态
    if payment.status == 'completed':
        messages.success(request, _('支付已完成'))
        return redirect('payment_success', wishlist_item_id=payment.wishlist_item.id)
    
    # 处理信用卡提交
    if request.method == 'POST':
        # 在真实环境中，这里应该从前端获取支付处理商提供的令牌
        # 而不是处理实际的信用卡信息
        card_token = request.POST.get('card_token', '')
        
        if not card_token:
            messages.error(request, _('支付信息不完整'))
            return redirect('credit_card_checkout', payment_id=payment_id)
        
        # 获取支付处理器
        processor = get_payment_processor(payment.payment_method.code)
        if not processor:
            messages.error(request, _('支付方式不可用'))
            return redirect('payment_method_list', wishlist_item_id=payment.wishlist_item.id)
        
        # 处理支付
        result = processor.process_payment(
            payment=payment,
            card_token=card_token
        )
        
        if result.get('success'):
            messages.success(request, _(result.get('message')))
            return redirect('payment_success', wishlist_item_id=payment.wishlist_item.id)
        else:
            messages.error(request, _(result.get('message')))
    
    context = {
        'payment': payment,
        'wishlist_item': payment.wishlist_item,
    }
    return render(request, 'payment/credit_card_checkout.html', context)


def payment_status(request, payment_id):
    """查询支付状态"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # 检查支付状态
    if payment.status == 'completed':
        return redirect('payment_success', wishlist_item_id=payment.wishlist_item.id)
    
    # 获取支付处理器
    processor = get_payment_processor(payment.payment_method.code)
    if not processor:
        messages.error(request, _('支付方式不可用'))
        return redirect('payment_method_list', wishlist_item_id=payment.wishlist_item.id)
    
    # 检查支付状态
    result = processor.check_payment_status(payment)
    
    # 如果支付已完成，重定向到成功页面
    if result.get('status') == 'completed':
        return redirect('payment_success', wishlist_item_id=payment.wishlist_item.id)
    
    context = {
        'payment': payment,
        'wishlist_item': payment.wishlist_item,
        'status_result': result,
    }
    return render(request, 'payment/payment_status.html', context)


def payment_success(request, wishlist_item_id):
    """支付成功页面"""
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    
    # 查找最新的成功支付
    try:
        payment = Payment.objects.filter(
            wishlist_item=wishlist_item,
            status='completed'
        ).latest('completed_at')
    except Payment.DoesNotExist:
        payment = None
    
    context = {
        'wishlist_item': wishlist_item,
        'payment': payment,
    }
    return render(request, 'payment/payment_success.html', context)


def payment_cancel(request, wishlist_item_id):
    """支付取消页面"""
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    
    # 查找最新的待处理支付并取消
    payments = Payment.objects.filter(
        wishlist_item=wishlist_item,
        status__in=['pending', 'processing']
    )
    
    for payment in payments:
        payment.status = 'cancelled'
        payment.status_message = '用户取消支付'
        payment.save(update_fields=['status', 'status_message'])
    
    context = {
        'wishlist_item': wishlist_item,
    }
    return render(request, 'payment/payment_cancel.html', context)


@csrf_exempt
def webhook_handler(request, payment_type):
    """支付Webhook处理"""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    # 根据支付类型获取对应的支付方式
    try:
        payment_method = PaymentMethod.objects.get(payment_type=payment_type, is_active=True)
    except PaymentMethod.DoesNotExist:
        logger.error(f"找不到支付方式: {payment_type}")
        return HttpResponse(status=404)
    
    # 获取支付处理器
    processor = get_payment_processor(payment_method.code)
    if not processor:
        logger.error(f"获取支付处理器失败: {payment_method.code}")
        return HttpResponse(status=500)
    
    # 处理webhook
    result = processor.process_webhook(request)
    
    # 返回结果
    if result.get('success'):
        return JsonResponse({'status': 'success', 'message': result.get('message')})
    else:
        return JsonResponse({'status': 'error', 'message': result.get('message')}, status=400)


@require_POST
@login_required
def check_payment_status_api(request, payment_id):
    """API接口: 检查支付状态"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # 获取支付处理器
    processor = get_payment_processor(payment.payment_method.code)
    if not processor:
        return JsonResponse({'success': False, 'message': '支付方式不可用'})
    
    # 检查支付状态
    result = processor.check_payment_status(payment)
    
    return JsonResponse(result)
