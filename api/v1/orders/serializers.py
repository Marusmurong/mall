from rest_framework import serializers
from order.models import Order, OrderItem, OrderLog, RefundDetail
from api.v1.products.serializers import GoodsListSerializer
from api.v1.users.serializers import ShippingAddressSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    product_data = GoodsListSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_data', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'total_price']

class OrderLogSerializer(serializers.ModelSerializer):
    """订单日志序列化器"""
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = OrderLog
        fields = ['id', 'action', 'status_from', 'status_to', 'note', 
                 'user', 'user_name', 'is_system', 'created_at']
        read_only_fields = ['id', 'created_at']

class RefundDetailSerializer(serializers.ModelSerializer):
    """退款详情序列化器"""
    processed_by_name = serializers.ReadOnlyField(source='processed_by.username')
    
    class Meta:
        model = RefundDetail
        fields = ['id', 'refund_amount', 'currency', 'refund_method', 
                 'status', 'reason', 'description', 'transaction_id', 
                 'processed_by', 'processed_by_name', 'processed_at', 
                 'receipt_image', 'requested_at', 'completed_at']
        read_only_fields = ['id', 'processed_by', 'processed_at', 'requested_at', 
                           'completed_at', 'transaction_id']

class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    logs = OrderLogSerializer(many=True, read_only=True)
    refund_details = RefundDetailSerializer(many=True, read_only=True)
    shipping_address_data = ShippingAddressSerializer(source='shipping_address', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'wishlist_item',
            'total_amount', 'currency', 'status', 
            'recipient_name', 'recipient_phone', 'shipping_address_text',
            'shipping_address', 'shipping_address_data',
            'is_anonymous_payer', 'payer_name', 'payer_email', 'payer_phone', 'payer_message',
            'payment_method', 'payment_platform', 'payment_time', 'payment_status',
            'tracking_number', 'shipping_carrier', 'shipping_method', 'shipping_cost',
            'shipped_at', 'delivered_at',
            'is_refunding', 'refund_status', 'refund_amount', 'refund_reason',
            'customer_notes', 'created_at', 'updated_at', 'completed_at',
            'items', 'logs', 'refund_details'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at', 'completed_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    """创建订单的序列化器"""
    items = serializers.ListField(
        child=serializers.DictField(), 
        write_only=True,
        required=False
    )
    shipping_address_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'wishlist_item', 'items', 'shipping_address_id',
            'recipient_name', 'recipient_phone', 'customer_notes',
            'is_anonymous_payer', 'payer_name', 'payer_email', 'payer_phone', 'payer_message'
        ]
    
    def validate(self, attrs):
        """验证订单数据"""
        from wishlist_new.models import WishlistItem
        from users.models import ShippingAddress
        from django.db.models import Sum
        
        # 检查必须提供wishlist_item或items中的一项
        if not attrs.get('wishlist_item') and not attrs.get('items'):
            raise serializers.ValidationError({"non_field_errors": "必须提供心愿单物品或普通商品项"})
        
        # 验证收货地址
        try:
            shipping_address = ShippingAddress.objects.get(
                id=attrs['shipping_address_id'],
                user=self.context['request'].user
            )
            attrs['shipping_address'] = shipping_address
            attrs['shipping_address_text'] = f"{shipping_address.country} {shipping_address.province} {shipping_address.city} {shipping_address.district} {shipping_address.address} {shipping_address.postal_code}"
        except ShippingAddress.DoesNotExist:
            raise serializers.ValidationError({"shipping_address_id": "收货地址不存在"})
        
        # 移除不需要的字段
        attrs.pop('shipping_address_id', None)
        
        return attrs
    
    def create(self, validated_data):
        """创建订单"""
        from goods.models import Goods
        from api.exceptions import BusinessException
        import uuid
        import datetime
        
        items_data = validated_data.pop('items', [])
        wishlist_item = validated_data.get('wishlist_item', None)
        
        # 生成订单号
        now = datetime.datetime.now()
        order_number = f"ORD{now.strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4().int)[:4]}"
        validated_data['order_number'] = order_number
        
        # 设置用户
        validated_data['user'] = self.context['request'].user
        
        # 计算订单总金额
        total_amount = 0
        
        # 创建订单
        order = Order.objects.create(**validated_data)
        
        # 如果是从心愿单创建
        if wishlist_item:
            total_amount = wishlist_item.price
            # 创建订单项
            if wishlist_item.product:
                OrderItem.objects.create(
                    order=order,
                    product=wishlist_item.product,
                    quantity=1,
                    price=wishlist_item.price
                )
        
        # 如果是普通商品创建
        for item_data in items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            try:
                product = Goods.objects.get(id=product_id)
                # 检查商品是否可见在当前站点
                if not product.is_visible_in_current_site():
                    raise BusinessException(f"商品 {product.name} 在当前站点不可见")
                
                # 创建订单项
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                
                # 计算金额
                total_amount += product.price * quantity
                
            except Goods.DoesNotExist:
                raise BusinessException(f"商品ID {product_id} 不存在")
        
        # 更新订单总金额
        order.total_amount = total_amount
        order.save()
        
        # 创建订单日志
        OrderLog.objects.create(
            order=order,
            action="创建订单",
            status_to="pending",
            is_system=True,
            note="用户创建了订单"
        )
        
        return order

class RefundCreateSerializer(serializers.ModelSerializer):
    """创建退款申请的序列化器"""
    class Meta:
        model = RefundDetail
        fields = ['refund_amount', 'refund_method', 'reason', 'description']
    
    def create(self, validated_data):
        order = self.context.get('order')
        if not order:
            raise serializers.ValidationError({"non_field_errors": "订单不存在"})
        
        if order.status not in ['paid', 'processing', 'shipped', 'delivered']:
            raise serializers.ValidationError({"non_field_errors": "当前订单状态不允许申请退款"})
        
        # 检查退款金额
        if validated_data['refund_amount'] > order.total_amount:
            raise serializers.ValidationError({"refund_amount": "退款金额不能大于订单总金额"})
        
        # 创建退款申请
        refund = RefundDetail.objects.create(
            order=order,
            payment=order.payment,
            currency=order.currency,
            **validated_data
        )
        
        # 更新订单状态
        order.is_refunding = True
        order.refund_status = 'pending'
        order.refund_reason = validated_data['reason']
        order.refund_amount = validated_data['refund_amount']
        order.save()
        
        # 创建订单日志
        OrderLog.objects.create(
            order=order,
            action="申请退款",
            status_from=order.status,
            status_to=order.status,
            is_system=False,
            user=self.context['request'].user,
            note=f"用户申请退款，金额: {validated_data['refund_amount']} {order.currency}"
        )
        
        return refund
