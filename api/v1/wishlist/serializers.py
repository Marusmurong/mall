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
    允许用户提供product_id和wishlist来添加商品到心愿单
    如果没有提供wishlist，将使用用户的第一个心愿单或创建新的
    """
    product_id = serializers.UUIDField(required=True, write_only=True)
    wishlist = serializers.UUIDField(required=False, write_only=True)
    
    class Meta:
        model = WishlistItem
        fields = [
            'product_id', 'wishlist', 'priority', 'description'
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
        
        # 检查请求数据中是否指定了心愿单ID
        wishlist_id = self.context['request'].data.get('wishlist')
        
        # 如果有指定心愿单ID，则使用该心愿单
        if wishlist_id:
            try:
                wishlist = Wishlist.objects.get(id=wishlist_id, user=user)
                print(f"使用指定的心愿单 ID: {wishlist_id}")
            except Wishlist.DoesNotExist:
                print(f"指定的心愿单 ID {wishlist_id} 不存在，将尝试使用第一个心愿单")
                wishlist_id = None
        
        # 如果没有指定心愿单ID或指定的心愿单不存在
        if not wishlist_id:
            # 获取用户的所有心愿单
            wishlists = Wishlist.objects.filter(user=user)
            
            # 如果用户有心愿单，使用第一个
            if wishlists.exists():
                wishlist = wishlists.first()
                print(f"使用用户的第一个心愿单 ID: {wishlist.id}")
            else:
                # 如果用户没有心愿单，创建一个新的
                wishlist = Wishlist.objects.create(
                    user=user,
                    name=f'{user.username}的心愿单'
                )
                print(f"为用户 {user.username} 创建了新的心愿单 ID: {wishlist.id}")
        
        # 允许在同一个心愿单中添加相同的商品
        # 之前的检查已移除，不再限制添加重复商品
        
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
