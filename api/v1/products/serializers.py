from rest_framework import serializers
from goods.models import Goods, GoodsImage

class GoodsImageSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    class Meta:
        model = GoodsImage
        fields = ['id', 'image', 'is_main', 'sort_order']

class GoodsListSerializer(serializers.ModelSerializer):
    """商品列表序列化器 - 精简版本"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Goods
        fields = [
            'id', 'name', 'price', 'original_price', 'image',
            'category', 'category_name', 'is_recommended', 'is_hot', 'is_new'
        ]

class GoodsDetailSerializer(serializers.ModelSerializer):
    """商品详情序列化器 - 完整版本"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = GoodsImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Goods
        fields = [
            'id', 'name', 'price', 'original_price', 'stock', 'sales',
            'category', 'category_name', 'image', 'images',
            'description', 'goods_desc', 'status',
            'is_recommended', 'is_hot', 'is_new',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['sales', 'created_at', 'updated_at']
