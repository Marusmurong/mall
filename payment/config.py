"""
支付模块配置文件
"""
from django.conf import settings

# USDT支付配置
USDT_CONFIG = {
    'wallet_address': getattr(settings, 'USDT_WALLET_ADDRESS', ''),
    'verification_key': getattr(settings, 'USDT_VERIFICATION_KEY', ''),
    'confirmation_count': getattr(settings, 'USDT_CONFIRMATION_COUNT', 6),
    'allowed_networks': getattr(settings, 'USDT_ALLOWED_NETWORKS', ['trc20', 'erc20', 'bep20']),
    'api_key': getattr(settings, 'USDT_API_KEY', ''),
    'api_secret': getattr(settings, 'USDT_API_SECRET', ''),
    'webhook_secret': getattr(settings, 'USDT_WEBHOOK_SECRET', ''),
}

# PayPal支付配置
PAYPAL_CONFIG = {
    'client_id': getattr(settings, 'PAYPAL_CLIENT_ID', ''),
    'client_secret': getattr(settings, 'PAYPAL_CLIENT_SECRET', ''),
    'mode': getattr(settings, 'PAYPAL_MODE', 'sandbox'),  # 'sandbox' 或 'live'
    'webhook_id': getattr(settings, 'PAYPAL_WEBHOOK_ID', ''),
}

# 信用卡支付配置 (使用Stripe作为示例)
CREDIT_CARD_CONFIG = {
    'provider': getattr(settings, 'CREDIT_CARD_PROVIDER', 'stripe'),
    'api_key': getattr(settings, 'CREDIT_CARD_API_KEY', ''),
    'api_secret': getattr(settings, 'CREDIT_CARD_API_SECRET', ''),
    'webhook_secret': getattr(settings, 'CREDIT_CARD_WEBHOOK_SECRET', ''),
    'success_url': getattr(settings, 'CREDIT_CARD_SUCCESS_URL', '/payment/success/'),
    'cancel_url': getattr(settings, 'CREDIT_CARD_CANCEL_URL', '/payment/cancel/'),
}

# 常规支付配置
PAYMENT_CONFIG = {
    'default_currency': getattr(settings, 'DEFAULT_CURRENCY', 'USD'),
    'available_currencies': getattr(settings, 'AVAILABLE_CURRENCIES', ['USD', 'EUR', 'USDT']),
    'exchange_rate_api_key': getattr(settings, 'EXCHANGE_RATE_API_KEY', ''),
    'payment_expiration_minutes': getattr(settings, 'PAYMENT_EXPIRATION_MINUTES', 60),  # 支付过期时间（分钟）
} 