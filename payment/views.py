from django.shortcuts import render
import json
import logging
from decimal import Decimal
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings

from wishlist_new.models import WishlistItem
from .models import Payment, PaymentMethod, PaymentWebhookLog, PayPalPaymentDetail, CoinbaseCommercePaymentDetail
from .processors import get_payment_processor, CoinbaseCommercePaymentProcessor

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
            # 检查是否为外部URL（以http开头）
            if checkout_url.startswith('http'):
                # 返回JSON响应，包含重定向URL
                return JsonResponse({
                    'success': True,
                    'payment_id': str(payment.id),
                    'payment_link': checkout_url,
                    'message': '支付已创建，请前往PayPal完成支付'
                })
            # 内部URL，使用普通重定向
            elif checkout_url.startswith('/'):
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


@login_required
def credit_card_checkout(request, payment_id):
    """信用卡支付结账页面"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # 如果不是本人创建的支付，不允许访问
    if payment.payer and payment.payer != request.user and not payment.is_anonymous:
        return HttpResponseForbidden("您没有权限访问此支付页面")
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payment/credit_card_checkout.html', context)


@login_required
def coinbase_commerce_checkout(request, payment_id):
    """Coinbase Commerce支付结账页面"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # 如果不是本人创建的支付，且不是匿名支付，则不允许访问
    if payment.payer and payment.payer != request.user and not payment.is_anonymous:
        return HttpResponseForbidden("您没有权限访问此支付页面")
    
    # 获取Coinbase支付详情
    try:
        coinbase_detail = payment.coinbase_details
        checkout_url = coinbase_detail.hosted_url
        
        # 如果有托管URL，重定向到Coinbase页面
        if checkout_url:
            return redirect(checkout_url)
    except Exception as e:
        logger.error(f"获取Coinbase支付详情失败: {str(e)}")
    
    # 如果没有托管URL或出错，显示自定义页面
    context = {
        'payment': payment,
        'coinbase_detail': getattr(payment, 'coinbase_details', None)
    }
    
    return render(request, 'payment/coinbase_commerce_checkout.html', context)


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
    """
    通用Webhook处理器，处理各种支付平台的回调
    支持的payment_type:
    - paypal: PayPal支付回调
    - coinbase: Coinbase Commerce回调
    """
    # 记录原始请求数据
    request_body = request.body.decode('utf-8')
    
    # 创建Webhook日志记录
    webhook_log = PaymentWebhookLog.objects.create(
        event_type=f"{payment_type}_webhook",
        payload=json.loads(request_body) if request_body else {},
        status='pending'
    )
    
    # 记录请求头信息
    request_headers = {}
    for key, value in request.headers.items():
        request_headers[key] = value
    webhook_log.payload['headers'] = request_headers
    webhook_log.save(update_fields=['payload'])
    
    logger.info(f"收到{payment_type}支付Webhook: {request_body[:200]}...")
    
    if payment_type == 'paypal':
        return handle_paypal_webhook(request, webhook_log)
    elif payment_type == 'coinbase':
        return handle_coinbase_webhook(request, webhook_log)
    else:
        logger.warning(f"不支持的支付类型Webhook: {payment_type}")
        webhook_log.status = 'failed'
        webhook_log.response = {'error': f'不支持的支付类型: {payment_type}'}
        webhook_log.save(update_fields=['status', 'response'])
        return JsonResponse({'status': 'error', 'message': f'不支持的支付类型: {payment_type}'})


def handle_paypal_webhook(request, webhook_log):
    """处理PayPal Webhook"""
    try:
        # 获取PayPal发送的事件通知
        event_type = request.headers.get('Paypal-Event-Type', '')
        event_body = json.loads(request.body.decode('utf-8'))
        
        # 更新webhook日志
        webhook_log.event_type = f"paypal_{event_type}"
        webhook_log.save(update_fields=['event_type'])
        
        # 验证webhook签名（实际项目中应该验证）
        # TODO: 实现验证逻辑
        
        # 提取PayPal事件数据
        resource_type = event_body.get('resource_type', '')
        event_data = event_body.get('resource', {})
        
        # 根据事件类型处理
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # 支付捕获完成
            transaction_id = event_data.get('id', '')
            payment_id = None
            
            # 尝试从custom_id或invoice_id找到对应的支付记录
            custom_id = event_data.get('custom_id', '')
            if custom_id:
                try:
                    payment = Payment.objects.get(id=custom_id)
                    payment_id = payment.id
                except Payment.DoesNotExist:
                    pass
            
            # 如果找不到custom_id，尝试通过invoice_id查找
            if not payment_id:
                invoice_id = event_data.get('invoice_id', '')
                if invoice_id:
                    try:
                        payment = Payment.objects.get(id=invoice_id)
                        payment_id = payment.id
                    except Payment.DoesNotExist:
                        pass
            
            # 如果找不到通过invoice_id，尝试通过关联的PayPal详情查找
            if not payment_id:
                paypal_order_id = event_data.get('supplementary_data', {}).get('related_ids', {}).get('order_id', '')
                if paypal_order_id:
                    try:
                        paypal_detail = PayPalPaymentDetail.objects.get(paypal_order_id=paypal_order_id)
                        payment = paypal_detail.payment
                        payment_id = payment.id
                    except PayPalPaymentDetail.DoesNotExist:
                        pass
            
            # 如果找到了支付记录，更新其状态
            if payment_id:
                payment = Payment.objects.get(id=payment_id)
                payment.mark_as_completed(transaction_id)
                
                # 如果有PayPal支付详情，更新其中的信息
                try:
                    paypal_detail = payment.paypal_details
                    paypal_detail.paypal_payer_id = event_data.get('payer', {}).get('payer_id', '')
                    paypal_detail.save(update_fields=['paypal_payer_id'])
                except:
                    pass
                
                webhook_log.status = 'completed'
                webhook_log.response = {
                    'status': 'success',
                    'message': '支付已完成',
                    'payment_id': str(payment_id)
                }
                webhook_log.save(update_fields=['status', 'response'])
                
                logger.info(f"PayPal支付完成: {payment_id}, 交易ID: {transaction_id}")
                return JsonResponse({'status': 'success', 'message': '支付已处理'})
            else:
                webhook_log.status = 'failed'
                webhook_log.response = {
                    'status': 'error',
                    'message': '找不到对应的支付记录'
                }
                webhook_log.save(update_fields=['status', 'response'])
                
                logger.warning(f"PayPal支付完成，但找不到对应的支付记录: {transaction_id}")
                return JsonResponse({'status': 'error', 'message': '找不到对应的支付记录'})
        
        # 其他PayPal事件类型
        webhook_log.status = 'skipped'
        webhook_log.response = {
            'status': 'success',
            'message': f'事件类型 {event_type} 不需要处理'
        }
        webhook_log.save(update_fields=['status', 'response'])
        
        return JsonResponse({'status': 'success', 'message': f'事件类型 {event_type} 不需要处理'})
    
    except Exception as e:
        logger.exception(f"处理PayPal webhook时出错: {str(e)}")
        webhook_log.status = 'failed'
        webhook_log.response = {
            'status': 'error',
            'message': f'处理PayPal webhook时出错: {str(e)}'
        }
        webhook_log.save(update_fields=['status', 'response'])
        
        return JsonResponse({'status': 'error', 'message': '内部服务器错误'})


def handle_coinbase_webhook(request, webhook_log):
    """处理Coinbase Commerce Webhook"""
    try:
        # 获取Coinbase发送的事件通知
        signature = request.headers.get('X-CC-Webhook-Signature', '')
        event_body = json.loads(request.body.decode('utf-8'))
        
        # 获取事件类型和ID
        event_type = event_body.get('event', {}).get('type', '')
        event_id = event_body.get('event', {}).get('id', '')
        
        # 更新webhook日志
        webhook_log.event_type = f"coinbase_{event_type}"
        webhook_log.save(update_fields=['event_type'])
        
        # 获取Coinbase API密钥用于验证
        webhook_secret = getattr(settings, 'COINBASE_COMMERCE_WEBHOOK_SECRET', '')
        
        # 验证webhook签名（实际项目中应该验证）
        # TODO: 实现验证逻辑
        # from coinbase_commerce.webhook import Webhook
        # if webhook_secret:
        #     try:
        #         event = Webhook.construct_event(request.body, signature, webhook_secret)
        #     except Exception as e:
        #         logger.warning(f"Coinbase webhook签名验证失败: {str(e)}")
        #         return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
        # 但这里我们先跳过验证
        
        # 提取charge和支付数据
        charge_data = event_body.get('event', {}).get('data', {})
        charge_id = charge_data.get('id', '')
        charge_code = charge_data.get('code', '')
        
        # 从metadata中获取payment_id
        metadata = charge_data.get('metadata', {})
        payment_id = metadata.get('payment_id', '')
        
        # 如果metadata中没有payment_id，尝试通过charge_id查找
        if not payment_id and charge_id:
            try:
                coinbase_detail = CoinbaseCommercePaymentDetail.objects.get(charge_id=charge_id)
                payment = coinbase_detail.payment
                payment_id = payment.id
            except CoinbaseCommercePaymentDetail.DoesNotExist:
                pass
        
        # 根据事件类型处理
        if event_type == 'charge:confirmed':
            # 支付确认
            if payment_id:
                payment = Payment.objects.get(id=payment_id)
                payment.mark_as_completed(charge_id)
                
                # 更新Coinbase支付详情
                try:
                    coinbase_detail = payment.coinbase_details
                    coinbase_detail.status = 'CONFIRMED'
                    coinbase_detail.crypto_used = charge_data.get('payments', [{}])[0].get('currency', '')
                    coinbase_detail.save(update_fields=['status', 'crypto_used'])
                except:
                    pass
                
                webhook_log.status = 'completed'
                webhook_log.response = {
                    'status': 'success',
                    'message': '支付已确认',
                    'payment_id': str(payment_id)
                }
                webhook_log.save(update_fields=['status', 'response'])
                
                logger.info(f"Coinbase支付确认: {payment_id}, Charge ID: {charge_id}")
                return JsonResponse({'status': 'success', 'message': '支付已处理'})
            else:
                webhook_log.status = 'failed'
                webhook_log.response = {
                    'status': 'error',
                    'message': '找不到对应的支付记录'
                }
                webhook_log.save(update_fields=['status', 'response'])
                
                logger.warning(f"Coinbase支付确认，但找不到对应的支付记录: {charge_id}")
                return JsonResponse({'status': 'error', 'message': '找不到对应的支付记录'})
        
        # 其他事件类型
        webhook_log.status = 'skipped'
        webhook_log.response = {
            'status': 'success',
            'message': f'事件类型 {event_type} 不需要处理'
        }
        webhook_log.save(update_fields=['status', 'response'])
        
        return JsonResponse({'status': 'success', 'message': f'事件类型 {event_type} 不需要处理'})
    
    except Exception as e:
        logger.exception(f"处理Coinbase webhook时出错: {str(e)}")
        webhook_log.status = 'failed'
        webhook_log.response = {
            'status': 'error',
            'message': f'处理Coinbase webhook时出错: {str(e)}'
        }
        webhook_log.save(update_fields=['status', 'response'])
        
        return JsonResponse({'status': 'error', 'message': '内部服务器错误'})


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


# 新增直接跳转视图
def payment_redirect(request, payment_id):
    """直接跳转到支付页面"""
    try:
        # 获取支付记录
        payment = get_object_or_404(Payment, id=payment_id)
        
        # 尝试获取支付链接
        payment_link = None
        
        # 1. 尝试从Coinbase支付详情获取
        try:
            if hasattr(payment, 'coinbase_details') and payment.coinbase_details and payment.coinbase_details.hosted_url:
                payment_link = payment.coinbase_details.hosted_url
                logger.info(f"从Coinbase支付详情获取支付链接: {payment_link}")
        except:
            pass
        
        # 2. 尝试从PayPal支付详情获取
        if not payment_link:
            try:
                if hasattr(payment, 'paypal_details') and payment.paypal_details and payment.paypal_details.payment_link:
                    payment_link = payment.paypal_details.payment_link
                    logger.info(f"从PayPal支付详情获取支付链接: {payment_link}")
            except:
                pass
        
        # 3. 尝试从payment_data中获取
        if not payment_link and payment.payment_data:
            if 'checkout_url' in payment.payment_data:
                payment_link = payment.payment_data.get('checkout_url')
                logger.info(f"从payment_data.checkout_url获取支付链接: {payment_link}")
            elif 'payment_link' in payment.payment_data:
                payment_link = payment.payment_data.get('payment_link')
                logger.info(f"从payment_data.payment_link获取支付链接: {payment_link}")
        
        # 如果找到支付链接，重定向
        if payment_link:
            logger.info(f"直接重定向到支付链接: {payment_link}")
            return redirect(payment_link)
        else:
            # 如果没有找到支付链接，返回错误信息
            logger.warning(f"未找到支付链接，payment_id: {payment_id}")
            messages.error(request, _('未找到支付链接'))
            return redirect('payment_status', payment_id=payment_id)
    
    except Exception as e:
        logger.exception(f"支付跳转错误: {str(e)}")
        messages.error(request, _(f'支付跳转错误: {str(e)}'))
        return redirect('/')
