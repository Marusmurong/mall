from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

# API文档信息配置
schema_view = get_schema_view(
    openapi.Info(
        title="Mall 多站点电商API",
        default_version='v1',
        description="Mall电商系统多站点API接口文档",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=settings.API_BASE_URL if hasattr(settings, 'API_BASE_URL') else None,
)
