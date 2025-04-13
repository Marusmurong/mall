from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from goods.models import GoodsCategory, Goods
from .serializers import CategorySerializer, CategoryTreeSerializer
from django.db.models import Q

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    商品分类API视图集
    提供分类列表、详情、树状结构等功能
    支持站点过滤
    """
    permission_classes = [permissions.AllowAny]  # 分类API允许公开访问
    serializer_class = CategorySerializer
    queryset = GoodsCategory.objects.filter(is_active=True).order_by('sort_order')
    
    def get_queryset(self):
        """
        根据站点获取分类列表
        不同站点可能显示不同的分类
        """
        queryset = super().get_queryset()
        
        # 检测是否在Swagger生成过程中
        if getattr(self, 'swagger_fake_view', False):
            # 在Swagger文档生成时返回简化的查询集
            return queryset
        
        # 获取站点代码
        site_code = self.request.GET.get('site', getattr(self.request, 'site_code', 'default'))
        
        # 查找此站点下有商品的分类
        if site_code:
            try:
                # 获取当前站点可见的所有商品
                # 修复数据库不支持contains操作符的问题
                site_products = Goods.objects.filter(
                    status='published'
                    # 暂时注释掉contains查询，返回所有商品
                    # Q(visible_in__contains=site_code) | 
                    # Q(visible_in=[]) | 
                    # Q(visible_in__isnull=True)
                )
                
                # 获取这些商品所属的分类ID
                category_ids = site_products.values_list('category_id', flat=True).distinct()
                
                # 筛选出这些分类及其父分类
                if category_ids:
                    # 包含这些分类ID
                    queryset = queryset.filter(
                        Q(id__in=category_ids) |  # 直接分类
                        Q(children__id__in=category_ids)  # 父分类
                    ).distinct()
            except Exception as e:
                # 捕获数据库后端不支持的查询错误
                print(f"Error in category filtering: {e}")
        
        # 支持按级别过滤
        level = self.request.query_params.get('level', None)
        if level and level.isdigit():
            queryset = queryset.filter(level=int(level))
            
        # 支持按父分类过滤
        parent = self.request.query_params.get('parent', None)
        if parent:
            if parent == 'null':
                queryset = queryset.filter(parent__isnull=True)
            elif parent.isdigit():
                queryset = queryset.filter(parent_id=int(parent))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        获取树状结构的分类数据
        只返回顶级分类，子分类通过递归方式获取
        """
        # 只获取顶级分类
        queryset = self.get_queryset().filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        获取指定分类下的商品列表
        """
        category = self.get_object()
        
        # 获取站点代码
        site_code = self.request.GET.get('site', getattr(self.request, 'site_code', 'default'))
        
        # 查询当前站点可见的商品
        products = Goods.objects.filter(
            Q(visible_in__contains=site_code) | 
            Q(visible_in=[]) | 
            Q(visible_in__isnull=True),
            status='published',
            category=category
        )
        
        # 分页处理
        page = self.paginate_queryset(products)
        
        from api.v1.products.serializers import GoodsListSerializer
        if page is not None:
            serializer = GoodsListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = GoodsListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
