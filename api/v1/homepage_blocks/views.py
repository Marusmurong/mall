from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Q
from content.models import HomeBlock
from .serializers import HomeBlockSerializer

class HomeBlockViewSet(viewsets.ReadOnlyModelViewSet):
    """
    首页模块/推荐楼层API视图集
    提供首页模块列表和详情功能
    支持按站点和模块类型过滤
    """
    permission_classes = [permissions.AllowAny]  # 首页模块API允许公开访问
    serializer_class = HomeBlockSerializer
    
    def get_queryset(self):
        """
        获取当前站点可见的首页模块
        支持按模块类型过滤
        """
        # 基础查询：激活状态
        queryset = HomeBlock.objects.filter(is_active=True)
        
        # 站点过滤 - 优先使用URL参数中的site
        site_code = self.request.GET.get('site', getattr(self.request, 'site_code', 'default'))
        
        # 只返回当前站点可见的模块
        # visible_in为空表示所有站点可见，否则当前站点必须在visible_in列表中
        queryset = queryset.filter(
            Q(visible_in__contains=site_code) | 
            Q(visible_in=[]) | 
            Q(visible_in__isnull=True)
        )
        
        # 按模块类型过滤
        block_type = self.request.query_params.get('block_type', None)
        if block_type:
            queryset = queryset.filter(block_type=block_type)
        
        # 排序
        return queryset.order_by('sort_order')
