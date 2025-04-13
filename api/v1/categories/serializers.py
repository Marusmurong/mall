from rest_framework import serializers
from goods.models import GoodsCategory

class CategorySerializer(serializers.ModelSerializer):
    """
    商品分类序列化器
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GoodsCategory
        fields = [
            'id', 'name', 'parent', 'parent_name', 'level', 
            'is_active', 'sort_order', 'description', 
            'product_count', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_product_count(self, obj):
        """
        获取分类下的商品数量
        """
        return obj.goods.filter(status='published').count()

class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    商品分类树状结构序列化器
    用于展示带有子分类的完整分类树
    """
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GoodsCategory
        fields = [
            'id', 'name', 'level', 'is_active', 
            'sort_order', 'description', 'product_count',
            'children'
        ]
    
    def get_children(self, obj):
        """
        递归获取子分类
        """
        children = obj.children.filter(is_active=True).order_by('sort_order')
        serializer = CategoryTreeSerializer(children, many=True, context=self.context)
        return serializer.data
    
    def get_product_count(self, obj):
        """
        获取分类下的商品数量
        """
        return obj.goods.filter(status='published').count()
