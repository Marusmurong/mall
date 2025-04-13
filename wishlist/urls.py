from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_list, name='list'),
    path('create/', views.create_wishlist, name='create'),
    path('<int:wishlist_id>/', views.wishlist_detail, name='detail'),
    path('add/<int:product_id>/', views.add_to_wishlist, name='add'),
    path('share/<uuid:share_code>/', views.share_wishlist, name='share'),
] 