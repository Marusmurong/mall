from rest_framework import serializers
from .models import PageContent, SiteSettings


class PageContentSerializer(serializers.ModelSerializer):
    """页面内容序列化器"""
    class Meta:
        model = PageContent
        fields = '__all__'


class PageContentListSerializer(serializers.ModelSerializer):
    """页面内容列表序列化器"""
    class Meta:
        model = PageContent
        fields = ['id', 'category', 'slug', 'title', 'is_active', 'updated_at']


class SiteSettingsSerializer(serializers.ModelSerializer):
    """站点设置序列化器"""
    class Meta:
        model = SiteSettings
        fields = '__all__'
