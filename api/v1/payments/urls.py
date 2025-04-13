from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentMethodViewSet, PaymentViewSet,
    USDTPaymentDetailView, PayPalPaymentDetailView
)

# 创建路由器并注册视图集
router = DefaultRouter()
router.register('methods', PaymentMethodViewSet, basename='payment-method')
router.register('list', PaymentViewSet, basename='payment')

# API URL配置
urlpatterns = [
    path('', include(router.urls)),
    
    # 支付详情API
    path('usdt-details/<uuid:payment_id>/', USDTPaymentDetailView.as_view(), name='usdt-payment-detail'),
    path('paypal-details/<uuid:payment_id>/', PayPalPaymentDetailView.as_view(), name='paypal-payment-detail'),
]
