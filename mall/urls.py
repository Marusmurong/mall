"""
URL configuration for mall project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from payment.views import webhook_handler

# 配置Swagger文档视图
schema_view = get_schema_view(
   openapi.Info(
      title="Mall API",
      default_version='v1',
      description="商城系统API文档",
      terms_of_service="https://www.yourapp.com/terms/",
      contact=openapi.Contact(email="contact@yourapp.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swagger文档URL - 恢复之前的配置
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^api/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    path('api/', include('site_templates.urls')),  # 站点配置 API
    path('api/v1/sites/', include('sites.urls')),  # 多站点管理 API
    path('api/v1/', include('api.v1.urls')),  # API v1 路由
    # 其他应用的URL
    path('users/', include('users.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('wishlist_new/', include('wishlist_new.urls')),
    path('order/', include('order.urls')),
    path('payment/', include('payment.urls')),
    path('telegram/', include('tg_bot.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 为了使MEDIA文件在开发期间可见
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 添加支付webhook URL
urlpatterns += [
    path('webhooks/payments/paypal/', webhook_handler, {'payment_type': 'paypal'}, name='paypal-webhook'),
    path('webhooks/payments/coinbase/', webhook_handler, {'payment_type': 'coinbase'}, name='coinbase-webhook'),
]
