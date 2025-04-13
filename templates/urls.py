from django.urls import path
from . import views

urlpatterns = [
    # 模板渲染视图
    path('', views.alokai_template_view, name='alokai_template'),
    path('admin/site-editor/', views.site_editor_view, name='site_editor'),
    path('admin/site-editor/<str:site_id>/', views.site_editor_view, name='site_editor_with_id'),
    
    # API路径
    path('api/v1/sites/<str:site_id>/config/', views.get_site_config, name='get_site_config'),
    path('api/v1/sites/<str:site_id>/blocks/', views.get_site_blocks, name='get_site_blocks'),
    path('api/v1/sites/', views.get_sites, name='get_sites'),
    path('api/v1/sites/<str:site_id>/config/update/', views.update_site_config, name='update_site_config'),
    path('api/v1/sites/<str:site_id>/blocks/update/', views.update_site_blocks, name='update_site_blocks'),
]
