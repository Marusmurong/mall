from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BannerViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register('', BannerViewSet, basename='banner')

# API URL配置
urlpatterns = [
    path('', include(router.urls)),
]
