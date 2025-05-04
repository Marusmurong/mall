from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PageContentViewSet, SiteSettingsViewSet

# 创建路由器
router = DefaultRouter()
router.register(r'page-contents', PageContentViewSet)
router.register(r'site-settings', SiteSettingsViewSet)

# URL 配置
urlpatterns = [
    path('', include(router.urls)),
    # 添加自定义动作的 URL
    path('page-contents/by_category_slug/', PageContentViewSet.as_view({'get': 'by_category_slug'})),
    path('site-settings/by_key/', SiteSettingsViewSet.as_view({'get': 'by_key'})),
]
