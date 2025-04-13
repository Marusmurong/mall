import logging
import uuid
import json
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
    CreditCardPaymentDetail
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
            # 为了演示，我们创建一个模拟的支付URL
            mock_paypal_url = f"/payment/paypal/checkout/{payment.id}/?order_id={paypal_order_id}"
            
            payment.payment_data = {
                'checkout_url': mock_paypal_url,
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


# 支付处理器工厂函数
def get_payment_processor(payment_method_code):
    """
    根据支付方式代码获取对应的支付处理器实例
    
    Args:
        payment_method_code: 支付方式代码
        
    Returns:
        支付处理器实例或None（如果找不到对应的支付方式）
    """
    logger = logging.getLogger(__name__)
    
    from .models import PaymentMethod
    
    try:
        payment_method = PaymentMethod.objects.get(code=payment_method_code, is_active=True)
    except PaymentMethod.DoesNotExist:
        logger.error(f"找不到支付方式: {payment_method_code}")
        return None
    
    # 根据支付方式类型返回对应的处理器
    try:
        if payment_method.payment_type == 'usdt':
            return USDTPaymentProcessor(payment_method)
        elif payment_method.payment_type == 'paypal':
            return PayPalPaymentProcessor(payment_method)
        elif payment_method.payment_type == 'credit_card':
            return CreditCardPaymentProcessor(payment_method)
        else:
            logger.error(f"不支持的支付类型: {payment_method.payment_type}")
            return None
    except Exception as e:
        logger.error(f"创建支付处理器时出错: {str(e)}")
        return None 