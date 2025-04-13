from rest_framework import serializers
from .models import Site, SiteTheme, SiteSlide, SiteConfig


class SiteThemeSerializer(serializers.ModelSerializer):
    """站点主题序列化器"""
    class Meta:
        model = SiteTheme
        exclude = ['id', 'site']


class SiteConfigSerializer(serializers.ModelSerializer):
    """站点配置序列化器"""
    class Meta:
        model = SiteConfig
        exclude = ['id', 'site']


class SiteSlideSerializer(serializers.ModelSerializer):
    """站点幻灯片序列化器"""
    class Meta:
        model = SiteSlide
        exclude = ['site']


class SiteSerializer(serializers.ModelSerializer):
    """站点基本信息序列化器"""
    class Meta:
        model = Site
        fields = ['id', 'name', 'code', 'domain', 'logo', 'favicon', 
                  'primary_color', 'secondary_color', 'frontend_url', 'frontend_port']


class SiteDetailSerializer(serializers.ModelSerializer):
    """站点详细信息序列化器"""
    theme = SiteThemeSerializer(read_only=True)
    config = SiteConfigSerializer(read_only=True)
    slides = SiteSlideSerializer(many=True, read_only=True)
    
    class Meta:
        model = Site
        fields = ['id', 'name', 'code', 'domain', 'description', 
                  'logo', 'favicon', 'primary_color', 'secondary_color',
                  'api_url', 'frontend_url', 'frontend_port', 
                  'theme', 'config', 'slides', 'created_at', 'updated_at']
