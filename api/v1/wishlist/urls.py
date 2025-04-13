from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet, WishlistItemViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register('lists', WishlistViewSet, basename='wishlist')
router.register('items', WishlistItemViewSet, basename='wishlist-item')

# API URL配置
urlpatterns = [
    path('', include(router.urls)),
    # 统计API
    path('stats/', WishlistViewSet.as_view({'get': 'stats_all'}), name='wishlist-stats-all'),
    # 检查商品是否在心愿单中
    path('check-product/<str:product_id>/', WishlistItemViewSet.as_view({'get': 'check_product_in_wishlist'}), name='check-product-in-wishlist'),
    # 获取用户的所有心愿单商品
    path('user-items/', WishlistItemViewSet.as_view({'get': 'user_items'}), name='user-wishlist-items'),
]
