from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet, RefundDetailViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register('list', OrderViewSet, basename='order')
router.register('items', OrderItemViewSet, basename='order-item')
router.register('refunds', RefundDetailViewSet, basename='order-refund')

# API URL配置
urlpatterns = [
    path('', include(router.urls)),
]
