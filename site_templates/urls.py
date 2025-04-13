from django.urls import path
from . import views

urlpatterns = [
    # API路由
    path('api/v1/sites/config/', views.get_site_config, name='get_site_config'),
]
