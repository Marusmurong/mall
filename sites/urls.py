from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import SiteViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'', SiteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
