from rest_framework import serializers
from wishlist_new.models import Wishlist, WishlistItem
from api.v1.products.serializers import GoodsListSerializer

class WishlistItemSerializer(serializers.ModelSerializer):
    """心愿单物品序列化器"""
    product_data = GoodsListSerializer(source='product', read_only=True)
    
    class Meta:
        model = WishlistItem
        fields = [
            'id', 'wishlist', 'product', 'product_data', 'title', 
            'description', 'price', 'currency', 'image', 'url',
            'priority', 'purchased', 'purchased_at', 'purchased_by',
            'payment_status', 'payment_completed', 'added_at'
        ]
        read_only_fields = ['id', 'added_at', 'purchased_by', 'purchased_at', 
                            'payment_status', 'payment_completed']

class WishlistSerializer(serializers.ModelSerializer):
    """心愿单序列化器"""
    items = WishlistItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'name', 'user', 'description', 'is_public', 
            'share_code', 'created_at', 'updated_at',
            'items', 'item_count'
        ]
        read_only_fields = ['id', 'user', 'share_code', 'created_at', 'updated_at']
    
    def get_item_count(self, obj):
        """获取心愿单物品数量"""
        return obj.items.count()
    
    def create(self, validated_data):
        """创建心愿单，自动关联当前用户"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WishlistItemCreateSerializer(serializers.ModelSerializer):
    """
    创建心愿单物品的序列化器
    允许用户仅提供product_id来添加商品到心愿单
    """
    product_id = serializers.UUIDField(required=True, write_only=True)
    
    class Meta:
        model = WishlistItem
        fields = [
            'product_id', 'priority', 'description'
        ]
        
    def create(self, validated_data):
        from goods.models import Goods
        from api.exceptions import BusinessException
        
        # 获取商品
        product_id = validated_data.pop('product_id')
        try:
            product = Goods.objects.get(id=product_id)
        except Goods.DoesNotExist:
            raise BusinessException("商品不存在")
        
        # 获取当前用户的心愿单
        user = self.context['request'].user
        wishlist, created = Wishlist.objects.get_or_create(
            user=user,
            defaults={'name': f'{user.username}的心愿单'}
        )
        
        # 检查商品是否已在心愿单中
        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            raise BusinessException("该商品已在心愿单中")
        
        # 创建心愿单物品
        wishlist_item = WishlistItem(
            wishlist=wishlist,
            product=product,
            title=product.name,
            price=product.price,
            description=validated_data.get('description', ''),
            priority=validated_data.get('priority', 'medium'),
        )
        
        # 如果商品有图片，则使用商品图片
        if product.image:
            wishlist_item.image = product.image
            
        wishlist_item.save()
        return wishlist_item
