import uuid
import json
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from wishlist_new.models import WishlistItem

# 支付方式选项
PAYMENT_TYPE_CHOICES = [
    ('usdt', 'USDT'),
    ('paypal', 'PayPal'),
    ('credit_card', 'Credit Card'),
    ('coinbase_commerce', 'Coinbase Commerce'),
]

# 支付状态选项
PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
]

# 默认货币
DEFAULT_CURRENCY = getattr(settings, 'DEFAULT_CURRENCY', 'USD')


class PaymentMethod(models.Model):
    """Payment Method Model"""
    name = models.CharField(max_length=100, help_text="Payment method name")
    code = models.CharField(max_length=50, unique=True, help_text="Payment method code")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, help_text="Payment type")
    description = models.TextField(blank=True, null=True, help_text="Payment method description")
    icon = models.ImageField(upload_to='payment_icons/', blank=True, null=True, help_text="Payment method icon")
    is_active = models.BooleanField(default=True, help_text="Is active")
    
    # 支付配置字段
    config = models.JSONField(default=dict, blank=True, help_text="Payment configuration parameters (API keys, etc.)")
    test_mode = models.BooleanField(default=True, help_text="Enable test mode")
    
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        
    def __str__(self):
        return self.name
    
    def get_config(self, key, default=None):
        """Get configuration parameter"""
        return self.config.get(key, default)
    
    def set_config(self, key, value):
        """Set configuration parameter"""
        if not self.config:
            self.config = {}
        self.config[key] = value


class Payment(models.Model):
    """Payment Record Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.CASCADE, related_name='payments', help_text="Related wishlist item", null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, help_text="Payment method")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount")
    currency = models.CharField(max_length=10, default=DEFAULT_CURRENCY, help_text="Currency")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', help_text="Payment status")
    status_message = models.CharField(max_length=255, blank=True, null=True, help_text="Status message")
    payment_data = models.JSONField(default=dict, help_text="Payment related data")
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text="Transaction ID")
    
    # 付款人信息
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', help_text="Payer")
    is_anonymous = models.BooleanField(default=False, help_text="Anonymous payment")
    payer_email = models.EmailField(blank=True, null=True, help_text="Payer email")
    payer_name = models.CharField(max_length=255, blank=True, null=True, help_text="Payer name")
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    updated_at = models.DateTimeField(auto_now=True, help_text="Updated at")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Completed at")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Record"
        verbose_name_plural = "Payment Records"
        
    def __str__(self):
        return f"{self.payment_method.name} - {self.amount} {self.currency}"
    
    def mark_as_completed(self, transaction_id=None):
        """Mark payment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        if transaction_id:
            self.transaction_id = transaction_id
            
        self.save(update_fields=['status', 'completed_at', 'transaction_id'])
        
        # 更新心愿单物品状态（如果有关联的心愿单物品）
        if self.wishlist_item:
            wishlist_item = self.wishlist_item
            wishlist_item.purchased = True
            wishlist_item.purchased_at = timezone.now()
            wishlist_item.purchased_by = self.payer
            wishlist_item.save(update_fields=['purchased', 'purchased_at', 'purchased_by'])
        
        return True


class USDTPaymentDetail(models.Model):
    """USDT Payment Details"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='usdt_details', help_text="Related payment record")
    wallet_address = models.CharField(max_length=255, help_text="Wallet address")
    network = models.CharField(max_length=20, default='trc20', help_text="USDT network")
    transaction_hash = models.CharField(max_length=255, blank=True, null=True, help_text="Transaction hash")
    sender_address = models.CharField(max_length=255, blank=True, null=True, help_text="Sender address")
    confirmation_count = models.PositiveIntegerField(default=0, help_text="Confirmation count")
    qr_code = models.ImageField(upload_to='payment_qrcodes/', blank=True, null=True, help_text="Payment QR code")
    
    class Meta:
        verbose_name = "USDT Payment Detail"
        verbose_name_plural = "USDT Payment Details"
        
    def __str__(self):
        return f"USDT - {self.payment.id}"


class PayPalPaymentDetail(models.Model):
    """PayPal Payment Details"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='paypal_details', help_text="Related payment record")
    paypal_order_id = models.CharField(max_length=255, blank=True, null=True, help_text="PayPal order ID")
    paypal_payer_id = models.CharField(max_length=255, blank=True, null=True, help_text="PayPal payer ID")
    payment_link = models.URLField(blank=True, null=True, help_text="Payment link")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Fee amount")
    
    class Meta:
        verbose_name = "PayPal Payment Detail"
        verbose_name_plural = "PayPal Payment Details"
        
    def __str__(self):
        return f"PayPal - {self.payment.id}"


class CreditCardPaymentDetail(models.Model):
    """Credit Card Payment Details"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='credit_card_details', help_text="Related payment record")
    processor = models.CharField(max_length=50, default='stripe', help_text="Processor")
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text="Transaction ID")
    card_type = models.CharField(max_length=50, blank=True, null=True, help_text="Card type")
    last_four = models.CharField(max_length=4, blank=True, null=True, help_text="Last four digits")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Fee amount")
    
    class Meta:
        verbose_name = "Credit Card Payment Detail"
        verbose_name_plural = "Credit Card Payment Details"
        
    def __str__(self):
        return f"Credit Card - {self.payment.id}"


class CoinbaseCommercePaymentDetail(models.Model):
    """Coinbase Commerce Payment Details"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='coinbase_commerce_details', help_text="Related payment record")
    charge_id = models.CharField(max_length=255, blank=True, null=True, help_text="Coinbase Charge ID")
    charge_code = models.CharField(max_length=255, blank=True, null=True, help_text="Coinbase Charge Code")
    hosted_url = models.URLField(blank=True, null=True, help_text="Payment hosted URL")
    status = models.CharField(max_length=50, blank=True, null=True, help_text="Coinbase payment status")
    crypto_used = models.CharField(max_length=50, blank=True, null=True, help_text="Cryptocurrency used")
    
    class Meta:
        verbose_name = "Coinbase Commerce Payment Detail"
        verbose_name_plural = "Coinbase Commerce Payment Details"
        
    def __str__(self):
        return f"Coinbase - {self.payment.id}"


class PaymentWebhookLog(models.Model):
    """Payment Webhook Log"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, help_text="Event type")
    payload = models.JSONField(default=dict, help_text="Original request data")
    response = models.JSONField(default=dict, help_text="Response data")
    status = models.CharField(max_length=20, default='pending', help_text="Processing status")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Created at")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Webhook Log"
        verbose_name_plural = "Webhook Logs"
        
    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
