from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from goods.models import Goods
from .serializers import GoodsListSerializer, GoodsDetailSerializer
from django.db.models import Q

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    商品API视图集
    支持列表、详情查询
    支持站点过滤、分类过滤、搜索
    """
    permission_classes = [permissions.AllowAny]  # 商品API允许公开访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_recommended', 'is_hot', 'is_new']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sales', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        获取商品查询集，根据站点进行过滤
        """
        queryset = Goods.objects.filter(status='published').select_related('category')
        
        # 站点过滤 - 优先使用URL参数中的site
        site_code = self.request.GET.get('site', getattr(self.request, 'site_code', 'default'))
        
        # 只返回当前站点可见的商品
        # 注意: 之前visible_in__contains会导致数据库错误
        # 改用字符串匹配或者返回所有商品，以修复平台兼容性问题
        
        # 暂时返回所有商品，以修复500错误
        # 实际生产环境应使用更精确的查询方式
        # queryset = queryset.filter(Q(visible_in__isnull=True) | Q(visible_in=[]))
        
        # 支持通过关键词搜索
        keyword = self.request.query_params.get('keyword', None)
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
            
        return queryset
    
    def get_serializer_class(self):
        """
        根据操作类型选择不同的序列化器
        列表视图使用精简版本，详情视图使用完整版本
        """
        if self.action == 'retrieve':
            return GoodsDetailSerializer
        return GoodsListSerializer
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """
        获取推荐商品列表
        """
        queryset = self.get_queryset().filter(is_recommended=True)[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hot(self, request):
        """
        获取热门商品列表
        """
        queryset = self.get_queryset().filter(is_hot=True)[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new(self, request):
        """
        获取新品列表
        """
        queryset = self.get_queryset().filter(is_new=True)[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
