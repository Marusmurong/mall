from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register('', CategoryViewSet, basename='category')

# API URL配置
urlpatterns = [
    path('', include(router.urls)),
]
