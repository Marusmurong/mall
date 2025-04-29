from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_sites, name='site-list'),
    path('<str:site_id>/config', views.site_config, name='site-config'),
    path('<str:site_id>/statistics', views.site_statistics, name='site-statistics'),
] 