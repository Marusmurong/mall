import logging
import uuid
import json
import requests
from abc import ABC, abstractmethod
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import (
    Payment, 
    PaymentMethod, 
    USDTPaymentDetail, 
    PayPalPaymentDetail,
    CreditCardPaymentDetail,
    CoinbaseCommercePaymentDetail
)

logger = logging.getLogger(__name__)


class PaymentProcessorBase(ABC):
    """支付处理器基类"""
    
    def __init__(self, payment_method):
        self.payment_method = payment_method
    
    @abstractmethod
    def create_payment(self, wishlist_item, amount, currency='USD', payer=None, **kwargs):
        """创建支付记录"""
        pass
    
    @abstractmethod
    def process_payment(self, payment, **kwargs):
        """处理支付"""
        pass
    
    @abstractmethod
    def check_payment_status(self, payment):
        """检查支付状态"""
        pass
    
    @abstractmethod
    def process_webhook(self, request):
        """处理webhook回调"""
        pass
    
    def _create_payment_base(self, wishlist_item, amount, currency='USD', payer=None, **kwargs):
        """创建基础支付记录"""
        reference_id = kwargs.get('reference_id', f"REF-{uuid.uuid4().hex[:8]}")
        is_anonymous = kwargs.get('is_anonymous', False)
        payer_email = kwargs.get('payer_email', '')
        payer_name = kwargs.get('payer_name', '')
        
        payment = Payment.objects.create(
            wishlist_item=wishlist_item,
            payment_method=self.payment_method,
            payer=None if is_anonymous else payer,
            amount=amount,
            currency=currency,
            reference_id=reference_id,
            is_anonymous=is_anonymous,
            payer_email=payer_email,
            payer_name=payer_name
        )
        
        return payment


class USDTPaymentProcessor(PaymentProcessorBase):
    """USDT支付处理器"""
    
    def __init__(self, payment_method):
        super().__init__(payment_method)
        # 从配置中获取支付参数
        self.wallet_address = payment_method.get_config('wallet_address', '')
        self.api_key = payment_method.get_config('api_key', '')
        self.api_secret = payment_method.get_config('api_secret', '')
        
    def create_payment(self, wishlist_item, amount, currency='USDT', payer=None, **kwargs):
        """创建USDT支付记录"""
        # 验证钱包地址
        if not self.wallet_address:
            return None
        
        # 创建基础支付记录
        payment = self._create_payment_base(
            wishlist_item=wishlist_item,
            amount=amount,
            currency=currency,
            payer=payer,
            **kwargs
        )
        
        # 创建USDT支付详情
        network = kwargs.get('network', 'trc20')
        
        usdt_details = USDTPaymentDetail.objects.create(
            payment=payment,
            wallet_address=self.wallet_address,
            network=network
        )
        
        return payment
    
    def process_payment(self, payment, **kwargs):
        """处理USDT支付
        通常情况下，USDT支付需要用户手动转账后提交交易哈希
        """
        transaction_hash = kwargs.get('transaction_hash')
        sender_address = kwargs.get('sender_address', '')
        
        if not transaction_hash:
            return {
                'success': False,
                'message': '请提供交易哈希'
            }
        
        try:
            usdt_details = payment.usdt_details
            usdt_details.transaction_hash = transaction_hash
            usdt_details.sender_address = sender_address
            usdt_details.save(update_fields=['transaction_hash', 'sender_address'])
            
            # 更新支付状态为处理中
            payment.status = 'processing'
            payment.status_message = '已提交交易哈希，等待确认中'
            payment.save(update_fields=['status', 'status_message'])
            
            # 在实际应用中，这里应该调用区块链API验证交易
            # 为了简化示例，我们假设交易已经有效
            
            return {
                'success': True,
                'message': '交易提交成功，等待确认'
            }
            
        except Exception as e:
            logger.error(f"处理USDT支付时出错: {str(e)}")
            return {
                'success': False,
                'message': f"处理支付时出错: {str(e)}"
            }
    
    def check_payment_status(self, payment):
        """检查USDT支付状态
        在实际应用中，这应该连接到区块链API检查交易状态
        """
        try:
            usdt_details = payment.usdt_details
            
            # 这里应该调用区块链API检查交易状态
            # 为了简化示例，我们假设交易已经确认
            if usdt_details.transaction_hash and payment.status == 'processing':
                # 模拟区块确认增加
                usdt_details.block_confirmation += 1
                usdt_details.save(update_fields=['block_confirmation'])
                
                if usdt_details.block_confirmation >= 1:  # 通常需要更多确认
                    payment.mark_as_completed(transaction_id=usdt_details.transaction_hash)
                    return {
                        'success': True,
                        'status': 'completed',
                        'message': '支付已完成'
                    }
            
            return {
                'success': True,
                'status': payment.status,
                'message': payment.status_message or '正在检查交易状态'
            }
            
        except Exception as e:
            logger.error(f"检查USDT支付状态时出错: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'message': f"检查支付状态时出错: {str(e)}"
            }
    
    def process_webhook(self, request):
        """处理USDT支付的webhook
        由于USDT通常不提供标准的webhook，这个方法通常是为了提供一致的接口
        实际实现可能需要依赖第三方服务
        """
        # USDT通常没有标准的webhook，可能需要自行实现监听区块链事件
        return {
            'success': False,
            'message': '暂不支持USDT的webhook'
        }


class PayPalPaymentProcessor(PaymentProcessorBase):
    """PayPal支付处理器"""
    
    def __init__(self, payment_method):
        super().__init__(payment_method)
        # 从配置中获取支付参数
        self.client_id = payment_method.get_config('client_id', '')
        self.client_secret = payment_method.get_config('client_secret', '')
        self.mode = payment_method.get_config('mode', 'sandbox')
        
    def create_payment(self, wishlist_item, amount, currency='USD', payer=None, **kwargs):
        """创建PayPal支付记录"""
        # 验证配置
        if not self.client_id or not self.client_secret:
            return None
        
        # 创建基础支付记录
        payment = self._create_payment_base(
            wishlist_item=wishlist_item,
            amount=amount,
            currency=currency,
            payer=payer,
            **kwargs
        )
        
        try:
            # 在实际应用中，这里应该调用PayPal API创建支付
            # 为了简化示例，我们创建一个模拟的PayPal订单ID
            paypal_order_id = f"PPORD-{uuid.uuid4().hex[:12]}"
            
            # 创建PayPal支付详情
            paypal_details = PayPalPaymentDetail.objects.create(
                payment=payment,
                paypal_order_id=paypal_order_id
            )
            
            # 构建PayPal支付URL (实际应用中应从PayPal API获取)
            return_url = kwargs.get('return_url', '')
            cancel_url = kwargs.get('cancel_url', '')
            
            # 通常这里应该调用PayPal API并获取重定向URL
            # 在实际应用中，此URL应为PayPal的实际结账页面URL
            # 这里模拟一个外部PayPal收银台URL
            external_paypal_url = ""
            
            # 如果是测试环境，使用测试URL
            if self.mode == 'sandbox':
                external_paypal_url = f"https://www.sandbox.paypal.com/checkoutnow?token={paypal_order_id}"
            else:
                external_paypal_url = f"https://www.paypal.com/checkoutnow?token={paypal_order_id}"
                
            # 设置回调URL
            mock_paypal_url = f"/payment/paypal/checkout/{payment.id}/?order_id={paypal_order_id}"
            
            payment.payment_data = {
                'checkout_url': external_paypal_url,  # 使用外部PayPal收银台URL
                'return_url': return_url,
                'cancel_url': cancel_url
            }
            payment.save(update_fields=['payment_data'])
            
            return payment
            
        except Exception as e:
            logger.error(f"创建PayPal支付时出错: {str(e)}")
            payment.status = 'failed'
            payment.status_message = f"创建PayPal支付时出错: {str(e)}"
            payment.save(update_fields=['status', 'status_message'])
            return payment
    
    def process_payment(self, payment, **kwargs):
        """处理PayPal支付
        通常在PayPal重定向用户回来后调用
        """
        paypal_payer_id = kwargs.get('paypal_payer_id')
        
        if not paypal_payer_id:
            return {
                'success': False,
                'message': '缺少PayPal支付者ID'
            }
        
        try:
            paypal_details = payment.paypal_details
            paypal_details.paypal_payer_id = paypal_payer_id
            paypal_details.save(update_fields=['paypal_payer_id'])
            
            # 在实际应用中，这里应该调用PayPal API执行/捕获支付
            # 为了简化示例，我们假设支付已经完成
            
            # 生成付款ID
            paypal_payment_id = f"PPPAY-{uuid.uuid4().hex[:12]}"
            paypal_details.paypal_payment_id = paypal_payment_id
            paypal_details.paypal_fee = payment.amount * Decimal('0.029') + Decimal('0.30')  # 模拟费用
            paypal_details.save(update_fields=['paypal_payment_id', 'paypal_fee'])
            
            # 标记支付为已完成
            payment.mark_as_completed(transaction_id=paypal_payment_id)
            
            return {
                'success': True,
                'message': '支付已完成'
            }
            
        except Exception as e:
            logger.error(f"处理PayPal支付时出错: {str(e)}")
            return {
                'success': False,
                'message': f"处理支付时出错: {str(e)}"
            }
    
    def check_payment_status(self, payment):
        """检查PayPal支付状态"""
        try:
            # 在实际应用中，这里应该调用PayPal API查询订单状态
            # 为了简化示例，我们直接返回数据库中的状态
            
            return {
                'success': True,
                'status': payment.status,
                'message': payment.status_message or '支付状态检查成功'
            }
            
        except Exception as e:
            logger.error(f"检查PayPal支付状态时出错: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'message': f"检查支付状态时出错: {str(e)}"
            }
    
    def process_webhook(self, request):
        """处理PayPal的webhook回调
        PayPal会发送事件通知，如付款成功、退款等
        """
        try:
            # 验证webhook签名
            # 在实际应用中，应该验证PayPal的webhook签名
            
            event_type = request.headers.get('Paypal-Event-Type', '')
            payload = json.loads(request.body)
            
            # 记录webhook
            from .models import PaymentWebhookLog
            webhook_log = PaymentWebhookLog.objects.create(
                payment_method=self.payment_method,
                event_type=event_type,
                payload=payload
            )
            
            # 处理不同的事件类型
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                resource = payload.get('resource', {})
                order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
                
                if order_id:
                    try:
                        paypal_detail = PayPalPaymentDetail.objects.get(paypal_order_id=order_id)
                        payment = paypal_detail.payment
                        
                        # 标记为已完成
                        payment.mark_as_completed(transaction_id=resource.get('id'))
                        
                        # 更新webhook日志
                        webhook_log.processed = True
                        webhook_log.related_payment = payment
                        webhook_log.save(update_fields=['processed', 'related_payment'])
                        
                        return {
                            'success': True,
                            'message': '支付已确认完成'
                        }
                    except PayPalPaymentDetail.DoesNotExist:
                        webhook_log.error_message = f"找不到对应的PayPal订单: {order_id}"
                        webhook_log.save(update_fields=['error_message'])
            
            return {
                'success': True,
                'message': f'已收到PayPal webhook: {event_type}'
            }
            
        except Exception as e:
            logger.error(f"处理PayPal webhook时出错: {str(e)}")
            return {
                'success': False,
                'message': f"处理webhook时出错: {str(e)}"
            }


class CreditCardPaymentProcessor(PaymentProcessorBase):
    """信用卡支付处理器"""
    
    def __init__(self, payment_method):
        super().__init__(payment_method)
        # 从配置中获取支付参数
        self.provider = payment_method.get_config('provider', 'stripe')
        self.api_key = payment_method.get_config('api_key', '')
        self.api_secret = payment_method.get_config('api_secret', '')
        
    def create_payment(self, wishlist_item, amount, currency='USD', payer=None, **kwargs):
        """创建信用卡支付记录"""
        # 验证配置
        if not self.api_key or not self.api_secret:
            return None
        
        # 创建基础支付记录
        payment = self._create_payment_base(
            wishlist_item=wishlist_item,
            amount=amount,
            currency=currency,
            payer=payer,
            **kwargs
        )
        
        try:
            # 创建信用卡支付详情
            cc_details = CreditCardPaymentDetail.objects.create(
                payment=payment,
                processor=self.provider
            )
            
            # 构建支付URL
            return_url = kwargs.get('return_url', '')
            cancel_url = kwargs.get('cancel_url', '')
            
            # 通常这里应该调用信用卡处理商的API并获取会话ID或结账URL
            # 为了演示，我们创建一个模拟的支付URL
            mock_cc_url = f"/payment/credit-card/checkout/{payment.id}/"
            
            payment.payment_data = {
                'checkout_url': mock_cc_url,
                'return_url': return_url,
                'cancel_url': cancel_url
            }
            payment.save(update_fields=['payment_data'])
            
            return payment
            
        except Exception as e:
            logger.error(f"创建信用卡支付时出错: {str(e)}")
            payment.status = 'failed'
            payment.status_message = f"创建信用卡支付时出错: {str(e)}"
            payment.save(update_fields=['status', 'status_message'])
            return payment
    
    def process_payment(self, payment, **kwargs):
        """处理信用卡支付
        处理来自支付表单的信用卡信息并发送到支付处理商
        注意：在实际应用中，不应直接处理信用卡信息，而应使用处理商的前端SDK
        """
        # 在真实环境中，这些信息应该由支付处理商前端SDK直接提交到处理商，避免接触敏感信息
        card_token = kwargs.get('card_token')  # 支付处理商提供的令牌，而不是实际的卡信息
        
        if not card_token:
            return {
                'success': False,
                'message': '缺少支付令牌'
            }
        
        try:
            cc_details = payment.credit_card_details
            
            # 在实际应用中，这里应该调用支付处理商API处理支付
            # 为了简化示例，我们假设支付已经完成
            
            # 假设处理商返回的信息
            mock_response = {
                'success': True,
                'transaction_id': f"CC-{uuid.uuid4().hex[:12]}",
                'card_type': 'Visa',
                'last_four': '4242',
                'authorization_code': f"AUTH-{uuid.uuid4().hex[:8]}",
                'fee': payment.amount * Decimal('0.029') + Decimal('0.30')  # 模拟费用
            }
            
            # 更新信用卡支付详情
            cc_details.card_type = mock_response['card_type']
            cc_details.last_four = mock_response['last_four']
            cc_details.authorization_code = mock_response['authorization_code']
            cc_details.processor_fee = mock_response['fee']
            cc_details.save()
            
            # 标记支付为已完成
            payment.mark_as_completed(transaction_id=mock_response['transaction_id'])
            
            return {
                'success': True,
                'message': '支付已完成'
            }
            
        except Exception as e:
            logger.error(f"处理信用卡支付时出错: {str(e)}")
            return {
                'success': False,
                'message': f"处理支付时出错: {str(e)}"
            }
    
    def check_payment_status(self, payment):
        """检查信用卡支付状态"""
        try:
            # 在实际应用中，这里应该调用支付处理商API查询交易状态
            # 为了简化示例，我们直接返回数据库中的状态
            
            return {
                'success': True,
                'status': payment.status,
                'message': payment.status_message or '支付状态检查成功'
            }
            
        except Exception as e:
            logger.error(f"检查信用卡支付状态时出错: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'message': f"检查支付状态时出错: {str(e)}"
            }
    
    def process_webhook(self, request):
        """处理信用卡支付处理商的webhook回调"""
        try:
            # 验证webhook签名
            # 在实际应用中，应该验证处理商的webhook签名
            
            # 假设处理的是Stripe的webhook
            payload = json.loads(request.body)
            event_type = payload.get('type', '')
            
            # 记录webhook
            from .models import PaymentWebhookLog
            webhook_log = PaymentWebhookLog.objects.create(
                payment_method=self.payment_method,
                event_type=event_type,
                payload=payload
            )
            
            # 处理不同的事件类型
            if event_type == 'charge.succeeded':
                transaction_id = payload.get('data', {}).get('object', {}).get('id')
                
                if transaction_id:
                    try:
                        payment = Payment.objects.get(transaction_id=transaction_id)
                        
                        # 标记为已完成（如果尚未完成）
                        if payment.status != 'completed':
                            payment.mark_as_completed()
                        
                        # 更新webhook日志
                        webhook_log.processed = True
                        webhook_log.related_payment = payment
                        webhook_log.save(update_fields=['processed', 'related_payment'])
                        
                        return {
                            'success': True,
                            'message': '付款已确认完成'
                        }
                    except Payment.DoesNotExist:
                        webhook_log.error_message = f"找不到对应的交易: {transaction_id}"
                        webhook_log.save(update_fields=['error_message'])
            
            return {
                'success': True,
                'message': f'已收到webhook: {event_type}'
            }
            
        except Exception as e:
            logger.error(f"处理信用卡webhook时出错: {str(e)}")
            return {
                'success': False,
                'message': f"处理webhook时出错: {str(e)}"
            }


class CoinbaseCommercePaymentProcessor(PaymentProcessorBase):
    """Coinbase Commerce支付处理器"""
    
    def __init__(self, payment_method):
        super().__init__(payment_method)
        # 从配置中获取支付参数
        self.api_key = payment_method.get_config('api_key', '')
        self.webhook_secret = payment_method.get_config('webhook_secret', '')
        self.checkout_style = payment_method.get_config('checkout_style', 'hosted')
        self.base_url = 'https://api.commerce.coinbase.com'
        
    def create_payment(self, wishlist_item, amount, currency='USD', payer=None, **kwargs):
        """创建Coinbase Commerce支付记录"""
        # 验证API密钥
        if not self.api_key:
            return None
        
        # 创建基础支付记录
        payment = self._create_payment_base(
            wishlist_item=wishlist_item,
            amount=amount,
            currency=currency,
            payer=payer,
            **kwargs
        )
        
        try:
            # 获取Coinbase商户名称和订单参考ID
            merchant_name = kwargs.get('merchant_name', 'Mall Store')
            reference_id = f"REF-{uuid.uuid4().hex[:8]}"
            
            # 构建商品描述
            product_name = wishlist_item.product.name if wishlist_item and hasattr(wishlist_item, 'product') else '心愿单商品'
            description = f"购买心愿单商品: {product_name}"
            
            # 构建重定向URL
            success_url = kwargs.get('success_url', '')
            cancel_url = kwargs.get('cancel_url', '')
            
            # 创建Coinbase Charge
            charge_data = {
                'name': product_name,
                'description': description,
                'pricing_type': 'fixed_price',
                'local_price': {
                    'amount': str(amount),
                    'currency': currency
                },
                'metadata': {
                    'customer_id': str(payer.id) if payer else 'guest',
                    'payment_id': str(payment.id),
                    'wishlist_item_id': str(wishlist_item.id) if wishlist_item else ''
                },
                'redirect_url': success_url,
                'cancel_url': cancel_url
            }
            
            # 模拟Coinbase API调用，实际应该调用真实API
            # 为演示目的，这里使用示例数据创建支付详情
            if settings.DEBUG or self.payment_method.test_mode:
                # 测试模式: 创建模拟数据
                charge_id = f"TEST-CHARGE-{uuid.uuid4().hex[:8]}"
                charge_code = f"TEST-CODE-{uuid.uuid4().hex[:6].upper()}"
                hosted_url = f"https://commerce.coinbase.com/checkout/demo-{uuid.uuid4().hex[:8]}"
            else:
                # 实际调用Coinbase API
                try:
                    headers = {
                        'X-CC-Api-Key': self.api_key,
                        'X-CC-Version': '2018-03-22',
                        'Content-Type': 'application/json'
                    }
                    response = requests.post(
                        f"{self.base_url}/charges",
                        headers=headers,
                        json=charge_data
                    )
                    
                    if response.status_code == 201:
                        data = response.json()['data']
                        charge_id = data['id']
                        charge_code = data['code']
                        hosted_url = data['hosted_url']
                    else:
                        logger.error(f"Coinbase API错误: {response.status_code} {response.text}")
                        payment.status = 'failed'
                        payment.status_message = f"Coinbase API错误: {response.status_code}"
                        payment.save(update_fields=['status', 'status_message'])
                        return payment
                except Exception as e:
                    logger.error(f"调用Coinbase API时出错: {str(e)}")
                    payment.status = 'failed'
                    payment.status_message = f"调用Coinbase API时出错: {str(e)}"
                    payment.save(update_fields=['status', 'status_message'])
                    return payment
            
            # 创建Coinbase支付详情
            coinbase_details = CoinbaseCommercePaymentDetail.objects.create(
                payment=payment,
                charge_id=charge_id,
                charge_code=charge_code,
                hosted_url=hosted_url,
                status='NEW'  # 初始状态
            )
            
            # 更新支付数据
            payment.payment_data = {
                'checkout_url': hosted_url
            }
            payment.save(update_fields=['payment_data'])
            
            return payment
            
        except Exception as e:
            logger.error(f"创建Coinbase Commerce支付时出错: {str(e)}")
            payment.status = 'failed'
            payment.status_message = f"创建支付时出错: {str(e)}"
            payment.save(update_fields=['status', 'status_message'])
            return payment
    
    def process_payment(self, payment, **kwargs):
        """处理Coinbase Commerce支付
        由于Coinbase Commerce是重定向到托管页面，此方法通常不会直接调用
        """
        return {
            'success': True,
            'message': '请前往Coinbase页面完成支付',
            'redirect_url': payment.payment_data.get('checkout_url', '')
        }
    
    def check_payment_status(self, payment):
        """检查Coinbase Commerce支付状态"""
        try:
            coinbase_details = payment.coinbase_details
            
            # 如果状态已经是完成，直接返回
            if payment.status == 'completed':
                return {
                    'success': True,
                    'status': 'completed',
                    'message': '支付已完成'
                }
            
            # 如果是测试模式，模拟检查结果
            if settings.DEBUG or self.payment_method.test_mode:
                # 固定返回待处理状态，实际应通过webhook更新
                return {
                    'success': True,
                    'status': 'pending',
                    'message': '支付处理中(测试模式)'
                }
            
            # 调用Coinbase API检查支付状态
            try:
                if not coinbase_details.charge_id:
                    return {
                        'success': False,
                        'status': 'error',
                        'message': '缺少Charge ID'
                    }
                
                headers = {
                    'X-CC-Api-Key': self.api_key,
                    'X-CC-Version': '2018-03-22'
                }
                response = requests.get(
                    f"{self.base_url}/charges/{coinbase_details.charge_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()['data']
                    coinbase_status = data['timeline'][-1]['status']
                    
                    # 更新支付详情状态
                    coinbase_details.status = coinbase_status
                    
                    # 如果使用了加密货币，记录使用的货币
                    if 'payments' in data and data['payments']:
                        coinbase_details.crypto_used = data['payments'][0]['value']['crypto']
                    
                    coinbase_details.save()
                    
                    # 如果支付已确认或完成，标记为已完成
                    if coinbase_status in ['COMPLETED', 'CONFIRMED']:
                        payment.mark_as_completed(transaction_id=coinbase_details.charge_id)
                        return {
                            'success': True,
                            'status': 'completed',
                            'message': '支付已完成'
                        }
                    
                    # 映射Coinbase状态到我们的状态
                    status_mapping = {
                        'NEW': 'pending',
                        'PENDING': 'pending',
                        'RESOLVED': 'completed',
                        'EXPIRED': 'failed',
                        'CANCELED': 'cancelled',
                        'UNRESOLVED': 'processing'
                    }
                    
                    internal_status = status_mapping.get(coinbase_status, 'processing')
                    
                    # 更新支付记录状态
                    payment.status = internal_status
                    payment.save(update_fields=['status'])
                    
                    return {
                        'success': True,
                        'status': internal_status,
                        'message': f'支付状态: {coinbase_status}'
                    }
                else:
                    logger.error(f"Coinbase API状态查询错误: {response.status_code} {response.text}")
                    return {
                        'success': False,
                        'status': 'error',
                        'message': f"API错误: {response.status_code}"
                    }
            except Exception as e:
                logger.error(f"检查Coinbase支付状态时出错: {str(e)}")
                return {
                    'success': False,
                    'status': 'error',
                    'message': f"检查状态时出错: {str(e)}"
                }
            
        except Exception as e:
            logger.error(f"获取Coinbase支付详情时出错: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'message': f"获取支付详情时出错: {str(e)}"
            }
    
    def process_webhook(self, request):
        """处理Coinbase Commerce webhook回调"""
        try:
            # 验证webhook签名
            signature = request.headers.get('X-CC-Webhook-Signature', '')
            
            if not signature and not settings.DEBUG:
                return {
                    'success': False,
                    'message': '缺少webhook签名'
                }
            
            # 在实际环境中应验证签名
            # 此处简化处理，假设签名有效
            
            # 解析webhook数据
            payload = json.loads(request.body)
            event_type = payload.get('type', '')
            
            if event_type not in ['charge:confirmed', 'charge:resolved', 'charge:failed', 'charge:created']:
                # 忽略其他类型的事件
                return {
                    'success': True,
                    'message': f'忽略事件类型: {event_type}'
                }
            
            # 获取charge数据
            charge_data = payload.get('data', {}).get('id', '')
            if not charge_data:
                return {
                    'success': False,
                    'message': '缺少charge数据'
                }
            
            charge_id = charge_data.get('id', '')
            
            # 查找对应的支付详情
            try:
                coinbase_detail = CoinbaseCommercePaymentDetail.objects.get(charge_id=charge_id)
                payment = coinbase_detail.payment
            except CoinbaseCommercePaymentDetail.DoesNotExist:
                return {
                    'success': False,
                    'message': f'未找到匹配的支付记录: {charge_id}'
                }
            
            # 根据事件类型更新状态
            coinbase_status = payload.get('data', {}).get('timeline', [{}])[-1].get('status', '')
            
            # 更新支付详情状态
            coinbase_detail.status = coinbase_status
            coinbase_detail.save(update_fields=['status'])
            
            # 如果使用了加密货币，记录使用的货币
            payments = payload.get('data', {}).get('payments', [])
            if payments:
                crypto = payments[0].get('value', {}).get('crypto', '')
                if crypto:
                    coinbase_detail.crypto_used = crypto
                    coinbase_detail.save(update_fields=['crypto_used'])
            
            # 如果支付已确认或完成，标记为已完成
            if coinbase_status in ['COMPLETED', 'CONFIRMED']:
                payment.mark_as_completed(transaction_id=charge_id)
            elif coinbase_status == 'CANCELED':
                payment.status = 'cancelled'
                payment.save(update_fields=['status'])
            elif coinbase_status == 'EXPIRED':
                payment.status = 'failed'
                payment.status_message = '支付已过期'
                payment.save(update_fields=['status', 'status_message'])
            
            return {
                'success': True,
                'message': f'已处理webhook事件: {event_type}'
            }
            
        except Exception as e:
            logger.error(f"处理Coinbase webhook时出错: {str(e)}")
            return {
                'success': False,
                'message': f"处理webhook时出错: {str(e)}"
            }


def get_payment_processor(payment_method_code):
    """根据支付方式代码获取对应的处理器"""
    try:
        payment_method = PaymentMethod.objects.get(code=payment_method_code, is_active=True)
    except PaymentMethod.DoesNotExist:
        return None
    
    # 根据支付类型返回对应的处理器
    if payment_method.payment_type == 'usdt':
        return USDTPaymentProcessor(payment_method)
    elif payment_method.payment_type == 'paypal':
        return PayPalPaymentProcessor(payment_method)
    elif payment_method.payment_type == 'credit_card':
        return CreditCardPaymentProcessor(payment_method)
    elif payment_method.payment_type == 'coinbase_commerce':
        return CoinbaseCommercePaymentProcessor(payment_method)
    else:
        return None 