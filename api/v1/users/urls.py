from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileView, UserRegisterView, ShippingAddressViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register('addresses', ShippingAddressViewSet, basename='address')

# API URL配置
urlpatterns = [
    # 用户信息API
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # 用户注册API
    path('register/', UserRegisterView.as_view(), name='user-register'),
    
    # 收货地址API
    path('', include(router.urls)),
]
