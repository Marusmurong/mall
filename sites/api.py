from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Site, SiteTheme, SiteSlide, SiteConfig
from .serializers import (
    SiteSerializer, SiteDetailSerializer, SiteThemeSerializer, 
    SiteSlideSerializer, SiteConfigSerializer
)


class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    站点API视图集
    """
    queryset = Site.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SiteDetailSerializer
        return SiteSerializer
    
    @action(detail=True, methods=['get'])
    def theme(self, request, pk=None):
        """获取站点主题配置"""
        site = self.get_object()
        theme = getattr(site, 'theme', None)
        if not theme:
            theme = SiteTheme.objects.create(site=site)
        
        serializer = SiteThemeSerializer(theme)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def config(self, request, pk=None):
        """获取站点配置"""
        site = self.get_object()
        config = getattr(site, 'config', None)
        if not config:
            config = SiteConfig.objects.create(site=site)
        
        serializer = SiteConfigSerializer(config)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def slides(self, request, pk=None):
        """获取站点幻灯片"""
        site = self.get_object()
        slides = site.slides.filter(is_active=True).order_by('order')
        
        serializer = SiteSlideSerializer(slides, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_code(self, request):
        """通过站点代码获取站点信息"""
        code = request.query_params.get('code')
        if not code:
            return Response({
                'code': 400,
                'message': '缺少站点代码参数',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        site = get_object_or_404(Site, code=code, is_active=True)
        serializer = SiteDetailSerializer(site)
        
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })
