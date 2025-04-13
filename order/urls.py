from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('create/', views.create_order, name='create'),
    path('detail/<int:order_id>/', views.order_detail, name='detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel'),
] 