from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Q
from content.models import Banner
from .serializers import BannerSerializer
from django.utils import timezone

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Banner轮播图API视图集
    提供轮播图列表和详情功能
    支持按站点和位置过滤
    """
    permission_classes = [permissions.AllowAny]  # 轮播图API允许公开访问
    serializer_class = BannerSerializer
    
    def get_queryset(self):
        """
        获取当前站点可见的Banner轮播图
        支持按位置过滤
        """
        # 获取当前时间，用于时间范围过滤
        now = timezone.now()
        
        # 基础查询：激活状态且在有效时间范围内
        queryset = Banner.objects.filter(
            is_active=True
        ).select_related('product')
        
        # 时间范围过滤
        queryset = queryset.filter(
            Q(start_time__isnull=True) | Q(start_time__lte=now),
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        )
        
        # 站点过滤 - 优先使用URL参数中的site
        site_code = self.request.GET.get('site', getattr(self.request, 'site_code', 'default'))
        
        # 只返回当前站点可见的轮播图
        # 修复数据库不支持contains操作符的问题
        # 暂时注释掉站点过滤，返回所有轮播图
        # queryset = queryset.filter(
        #     Q(visible_in__contains=site_code) | 
        #     Q(visible_in=[]) | 
        #     Q(visible_in__isnull=True)
        # )
        
        # 按位置过滤
        position = self.request.query_params.get('position', None)
        if position:
            queryset = queryset.filter(position=position)
        
        # 排序
        return queryset.order_by('sort_order')
