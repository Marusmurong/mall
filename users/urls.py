from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('network/', views.invitation_network_view, name='invitation_network'),
    path('invitee/<int:user_id>/', views.invitee_detail_view, name='invitee_detail'),
    
    # 封号相关的URL
    path('ban-notice/', views.ban_notice_view, name='ban_notice'),
    path('admin/ban-user/<int:user_id>/', views.ban_user_view, name='ban_user'),
    path('admin/unban-user/<int:user_id>/', views.unban_user_view, name='unban_user'),
    path('api/user/<int:user_id>/ban-status/', views.user_ban_status_api, name='user_ban_status_api'),
] 