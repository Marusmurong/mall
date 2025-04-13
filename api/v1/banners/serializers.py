from rest_framework import serializers
from content.models import Banner
from api.v1.products.serializers import GoodsListSerializer

class BannerSerializer(serializers.ModelSerializer):
    """Banner轮播图序列化器"""
    product_data = GoodsListSerializer(source='product', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'image', 'image_url', 'link', 
            'product', 'product_data', 'position',
            'sort_order', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """获取图片完整URL"""
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
