from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PageContent, SiteSettings
from .serializers import PageContentSerializer, PageContentListSerializer, SiteSettingsSerializer

class PageContentViewSet(viewsets.ModelViewSet):
    """页面内容接口"""
    queryset = PageContent.objects.filter(is_active=True)
    serializer_class = PageContentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['category', 'slug']
    search_fields = ['title', 'content', 'slug']
    ordering_fields = ['sort_order', 'created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PageContentListSerializer
        return PageContentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 按分类过滤
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # 按站点可见性过滤
        site = self.request.query_params.get('site')
        if site:
            queryset = queryset.filter(visible_in__contains=[site])
        
        return queryset.order_by('sort_order')
    
    @action(detail=False, methods=['get'])
    def by_category_slug(self, request):
        """按分类和slug获取内容"""
        category = request.query_params.get('category')
        slug = request.query_params.get('slug')
        
        if not category or not slug:
            return Response(
                {"error": "必须提供category和slug参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            page_content = PageContent.objects.get(
                category=category, 
                slug=slug,
                is_active=True
            )
            serializer = self.get_serializer(page_content)
            return Response(serializer.data)
        except PageContent.DoesNotExist:
            return Response(
                {"error": f"未找到指定的内容: {category}/{slug}"},
                status=status.HTTP_404_NOT_FOUND
            )

class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """站点设置接口"""
    queryset = SiteSettings.objects.filter(is_active=True)
    serializer_class = SiteSettingsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['key']
    
    @action(detail=False, methods=['get'])
    def by_key(self, request):
        """按键名获取设置值"""
        key = request.query_params.get('key')
        
        if not key:
            return Response(
                {"error": "必须提供key参数"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            setting = SiteSettings.objects.get(key=key, is_active=True)
            serializer = self.get_serializer(setting)
            return Response(serializer.data)
        except SiteSettings.DoesNotExist:
            return Response(
                {"error": f"未找到指定的设置: {key}"},
                status=status.HTTP_404_NOT_FOUND
            )
