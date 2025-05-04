from rest_framework import serializers
from payment.models import (
    Payment, PaymentMethod, USDTPaymentDetail, 
    PayPalPaymentDetail, CreditCardPaymentDetail
)
from api.exceptions import BusinessException

class PaymentMethodSerializer(serializers.ModelSerializer):
    """支付方式序列化器"""
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'code', 'payment_type', 'description', 'icon', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

class USDTPaymentDetailSerializer(serializers.ModelSerializer):
    """USDT支付详情序列化器"""
    class Meta:
        model = USDTPaymentDetail
        fields = ['id', 'payment', 'wallet_address', 'network', 
                 'transaction_hash', 'sender_address', 'confirmation_count', 'qr_code']
        read_only_fields = ['id', 'payment', 'wallet_address', 'qr_code']

class PayPalPaymentDetailSerializer(serializers.ModelSerializer):
    """PayPal支付详情序列化器"""
    class Meta:
        model = PayPalPaymentDetail
        fields = ['id', 'payment', 'paypal_order_id', 'paypal_payer_id', 
                 'payment_link', 'fee_amount']
        read_only_fields = ['id', 'payment', 'paypal_order_id', 'payment_link']

class CreditCardPaymentDetailSerializer(serializers.ModelSerializer):
    """信用卡支付详情序列化器"""
    class Meta:
        model = CreditCardPaymentDetail
        fields = ['id', 'payment', 'processor', 'transaction_id',
                 'card_type', 'last_four', 'fee_amount']
        read_only_fields = ['id', 'payment', 'transaction_id', 'card_type', 'last_four']

class PaymentSerializer(serializers.ModelSerializer):
    """支付记录序列化器"""
    payment_method_data = PaymentMethodSerializer(source='payment_method', read_only=True)
    usdt_details = USDTPaymentDetailSerializer(read_only=True)
    paypal_details = PayPalPaymentDetailSerializer(read_only=True)
    credit_card_details = CreditCardPaymentDetailSerializer(read_only=True)
    payment_link = serializers.SerializerMethodField(read_only=True)
    checkout_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'wishlist_item', 'payment_method', 'payment_method_data',
            'amount', 'currency', 'status', 'status_message', 
            'transaction_id', 'payer', 'is_anonymous', 'payer_email', 
            'payer_name', 'created_at', 'updated_at', 'completed_at',
            'usdt_details', 'paypal_details', 'credit_card_details',
            'payment_link', 'checkout_url', 'payment_data'
        ]
        read_only_fields = ['id', 'status', 'transaction_id', 'created_at', 
                           'updated_at', 'completed_at']
                           
    def get_payment_link(self, obj):
        """获取支付链接"""
        # 首先检查PayPal支付详情
        try:
            if hasattr(obj, 'paypal_details') and obj.paypal_details and obj.paypal_details.payment_link:
                return obj.paypal_details.payment_link
        except:
            pass
        
        # 检查Coinbase支付详情
        try:
            if hasattr(obj, 'coinbase_details') and obj.coinbase_details and obj.coinbase_details.hosted_url:
                return obj.coinbase_details.hosted_url
        except:
            pass
            
        # 然后检查支付数据中是否有支付链接
        if obj.payment_data and 'checkout_url' in obj.payment_data:
            return obj.payment_data.get('checkout_url')
            
        if obj.payment_data and 'payment_link' in obj.payment_data:
            return obj.payment_data.get('payment_link')
            
        # 最后检查从payment/utils.py中获取
        try:
            from payment.utils import get_payment_checkout_url
            return get_payment_checkout_url(obj)
        except:
            return None
            
    def get_checkout_url(self, obj):
        """获取结账URL"""
        # 检查支付数据中是否有结账URL
        if obj.payment_data and 'checkout_url' in obj.payment_data:
            checkout_url = obj.payment_data.get('checkout_url')
            
            # 如果是相对URL，转换为绝对URL
            if checkout_url and checkout_url.startswith('/'):
                from django.conf import settings
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                return f"{base_url}{checkout_url}"
                
            return checkout_url
            
        return None
        
    def to_representation(self, instance):
        """自定义响应格式，确保支付链接可以直接获取到"""
        ret = super().to_representation(instance)
        
        # 确保payment_link字段优先显示在响应中
        payment_link = self.get_payment_link(instance)
        if payment_link:
            ret['payment_link'] = payment_link
            
        return ret

class PaymentCreateSerializer(serializers.ModelSerializer):
    """创建支付记录的序列化器"""
    wishlist_item_id = serializers.UUIDField(required=True, write_only=True)
    payment_method_id = serializers.IntegerField(required=True, write_only=True)
    order_id = serializers.UUIDField(required=False, write_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'wishlist_item_id', 'payment_method_id', 'order_id',
            'amount', 'currency', 'is_anonymous', 'payer_email', 
            'payer_name'
        ]
    
    def validate(self, attrs):
        """验证支付数据"""
        from wishlist_new.models import WishlistItem
        from order.models import Order
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # 验证付款人
        if attrs.get('is_anonymous', False) and not attrs.get('payer_email'):
            raise serializers.ValidationError({"payer_email": "匿名支付需要提供邮箱"})
        
        # 验证支付方式
        try:
            payment_method = PaymentMethod.objects.get(
                id=attrs.pop('payment_method_id'),
                is_active=True
            )
            attrs['payment_method'] = payment_method
        except PaymentMethod.DoesNotExist:
            raise serializers.ValidationError({"payment_method_id": "支付方式不存在或未启用"})
        
        # 验证心愿单物品
        wishlist_item_id = attrs.pop('wishlist_item_id', None)
        if wishlist_item_id:
            try:
                wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
                
                # 检查是否已经支付过
                if wishlist_item.purchased:
                    raise serializers.ValidationError({"wishlist_item_id": "该心愿单物品已被购买"})
                
                attrs['wishlist_item'] = wishlist_item
                
                # 如果没有提供金额，使用心愿单物品的价格
                if not attrs.get('amount'):
                    attrs['amount'] = wishlist_item.price
                    
            except WishlistItem.DoesNotExist:
                raise serializers.ValidationError({"wishlist_item_id": "心愿单物品不存在"})
        
        # 验证订单
        order_id = attrs.pop('order_id', None)
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                
                # 如果关联订单，保存到payment_data
                attrs['payment_data'] = {
                    'order_id': str(order.id),
                    'order_number': order.order_number
                }
                
                # 如果没有提供金额，使用订单的总金额
                if not attrs.get('amount'):
                    attrs['amount'] = order.total_amount
                    
            except Order.DoesNotExist:
                raise serializers.ValidationError({"order_id": "订单不存在"})
                
        # 设置付款人 - 修改这里以支持匿名支付
        if not attrs.get('is_anonymous', False):
            # 只有当用户登录时才设置付款人
            if 'request' in self.context and self.context['request'].user.is_authenticated:
                attrs['payer'] = self.context['request'].user
            else:
                # 未登录用户设置为匿名支付
                attrs['is_anonymous'] = True
                
        return attrs
    
    def create(self, validated_data):
        """创建支付记录"""
        # 创建基本支付记录
        payment = Payment.objects.create(**validated_data)
        
        # 根据支付方式创建对应的支付详情
        payment_method = validated_data['payment_method']
        
        if payment_method.payment_type == 'usdt':
            # 创建USDT支付详情
            from payment.utils import generate_usdt_payment_details
            generate_usdt_payment_details(payment)
            
        elif payment_method.payment_type == 'paypal':
            # 创建PayPal支付详情
            from payment.utils import generate_paypal_payment_details
            generate_paypal_payment_details(payment)
            
        elif payment_method.payment_type == 'credit_card':
            # 创建信用卡支付详情
            from payment.utils import generate_credit_card_payment_details
            generate_credit_card_payment_details(payment)
            
        elif payment_method.payment_type == 'coinbase' or payment_method.code == 'coinbase_commerce':
            # 创建Coinbase支付详情
            from payment.utils import generate_coinbase_payment_details
            generate_coinbase_payment_details(payment)
            
        return payment

class PaymentVerifySerializer(serializers.Serializer):
    """验证支付的序列化器"""
    payment_id = serializers.UUIDField(required=True)
    transaction_hash = serializers.CharField(required=False)
    paypal_order_id = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """验证支付ID并检查状态"""
        payment_id = attrs.get('payment_id')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            # 检查支付状态
            if payment.status == 'completed':
                raise serializers.ValidationError({"payment_id": "该支付已完成"})
                
            if payment.status == 'cancelled':
                raise serializers.ValidationError({"payment_id": "该支付已取消"})
                
            # 将支付对象添加到上下文中
            self.context['payment'] = payment
            
        except Payment.DoesNotExist:
            raise serializers.ValidationError({"payment_id": "支付记录不存在"})
            
        return attrs
