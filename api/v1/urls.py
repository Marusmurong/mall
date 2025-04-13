from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 创建默认路由器
router = DefaultRouter()

# API URL配置
urlpatterns = [
    # 使用路由器自动注册的URL
    path('', include(router.urls)),
    
    # 认证API
    path('auth/', include('api.v1.auth.urls')),
    
    # 商品系统API
    path('products/', include('api.v1.products.urls')),
    
    # 分类 API
    path('categories/', include('api.v1.categories.urls')),
    # 品牌 API - 待实现
    # path('brands/', include('api.v1.brands.urls')),
    
    # 首页内容块API
    path('banners/', include('api.v1.banners.urls')),
    path('homepage-blocks/', include('api.v1.homepage_blocks.urls')),
    
    # 用户系统API
    path('user/', include('api.v1.users.urls')),
    
    # 心愿单功能API
    path('wishlist/', include('api.v1.wishlist.urls')),
    
    # 订单/支付API
    path('orders/', include('api.v1.orders.urls')),
    path('payments/', include('api.v1.payments.urls')),
    
    # 推荐/BI/行为绘点API - 待实现
    # path('recommendations/', include('api.v1.recommendations.urls')),
    # path('events/', include('api.v1.events.urls')),
]
