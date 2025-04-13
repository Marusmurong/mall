from django.urls import path
from . import views

urlpatterns = [
    # 选择支付方式
    path('method-list/<int:wishlist_item_id>/', views.payment_method_list, name='payment_method_list'),
    
    # 创建支付
    path('create/<int:wishlist_item_id>/', views.create_payment, name='create_payment'),
    
    # 支付详情页面
    path('usdt/<int:payment_id>/', views.usdt_payment_detail, name='usdt_payment_detail'),
    path('paypal/<int:payment_id>/', views.paypal_checkout, name='paypal_checkout'),
    path('credit-card/<int:payment_id>/', views.credit_card_checkout, name='credit_card_checkout'),
    
    # 支付状态
    path('status/<int:payment_id>/', views.payment_status, name='payment_status'),
    path('api/status/<int:payment_id>/', views.check_payment_status_api, name='check_payment_status_api'),
    
    # 支付结果
    path('success/<int:wishlist_item_id>/', views.payment_success, name='payment_success'),
    path('cancel/<int:wishlist_item_id>/', views.payment_cancel, name='payment_cancel'),
    
    # Webhook接口
    path('webhook/<str:payment_type>/', views.webhook_handler, name='webhook_handler'),
] 