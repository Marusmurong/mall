from rest_framework import serializers
from content.models import HomeBlock

class HomeBlockSerializer(serializers.ModelSerializer):
    """首页模块/推荐楼层序列化器"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = HomeBlock
        fields = [
            'id', 'title', 'subtitle', 'block_type',
            'content', 'image', 'image_url', 'link',
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
