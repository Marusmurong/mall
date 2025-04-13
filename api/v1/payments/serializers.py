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
    
    class Meta:
        model = Payment
        fields = [
            'id', 'wishlist_item', 'payment_method', 'payment_method_data',
            'amount', 'currency', 'status', 'status_message', 
            'transaction_id', 'payer', 'is_anonymous', 'payer_email', 
            'payer_name', 'created_at', 'updated_at', 'completed_at',
            'usdt_details', 'paypal_details', 'credit_card_details'
        ]
        read_only_fields = ['id', 'status', 'transaction_id', 'created_at', 
                           'updated_at', 'completed_at']

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
                
        # 设置付款人
        if not attrs.get('is_anonymous', False) and self.context['request'].user.is_authenticated:
            attrs['payer'] = self.context['request'].user
            
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
