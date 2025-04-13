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
    ('credit_card', '信用卡'),
]

# 支付状态选项
PAYMENT_STATUS_CHOICES = [
    ('pending', '待处理'),
    ('processing', '处理中'),
    ('completed', '已完成'),
    ('failed', '失败'),
    ('cancelled', '已取消'),
]

# 默认货币
DEFAULT_CURRENCY = getattr(settings, 'DEFAULT_CURRENCY', 'USD')


class PaymentMethod(models.Model):
    """支付方式模型"""
    name = models.CharField(max_length=100, help_text="支付方式名称")
    code = models.CharField(max_length=50, unique=True, help_text="支付方式代码")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, help_text="支付类型")
    description = models.TextField(blank=True, null=True, help_text="支付方式描述")
    icon = models.ImageField(upload_to='payment_icons/', blank=True, null=True, help_text="支付方式图标")
    is_active = models.BooleanField(default=True, help_text="是否启用")
    
    # 支付配置字段
    config = models.JSONField(default=dict, blank=True, help_text="支付配置参数（API密钥等）")
    test_mode = models.BooleanField(default=True, help_text="是否启用测试模式")
    
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    
    class Meta:
        ordering = ['name']
        verbose_name = "支付方式"
        verbose_name_plural = "支付方式"
        
    def __str__(self):
        return self.name
    
    def get_config(self, key, default=None):
        """获取配置参数"""
        return self.config.get(key, default)
    
    def set_config(self, key, value):
        """设置配置参数"""
        if not self.config:
            self.config = {}
        self.config[key] = value


class Payment(models.Model):
    """支付记录模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.CASCADE, related_name='payments', help_text="关联的心愿单物品", null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, help_text="支付方式")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="支付金额")
    currency = models.CharField(max_length=10, default=DEFAULT_CURRENCY, help_text="货币")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', help_text="支付状态")
    status_message = models.CharField(max_length=255, blank=True, null=True, help_text="状态消息")
    payment_data = models.JSONField(default=dict, help_text="支付相关数据")
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text="交易ID")
    
    # 付款人信息
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', help_text="付款人")
    is_anonymous = models.BooleanField(default=False, help_text="是否匿名支付")
    payer_email = models.EmailField(blank=True, null=True, help_text="付款人邮箱")
    payer_name = models.CharField(max_length=255, blank=True, null=True, help_text="付款人姓名")
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="完成时间")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "支付记录"
        verbose_name_plural = "支付记录"
        
    def __str__(self):
        return f"{self.payment_method.name} - {self.amount} {self.currency}"
    
    def mark_as_completed(self, transaction_id=None):
        """标记支付为完成状态"""
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
    """USDT支付详情"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='usdt_details', help_text="关联的支付记录")
    wallet_address = models.CharField(max_length=255, help_text="钱包地址")
    network = models.CharField(max_length=20, default='trc20', help_text="USDT网络")
    transaction_hash = models.CharField(max_length=255, blank=True, null=True, help_text="交易哈希")
    sender_address = models.CharField(max_length=255, blank=True, null=True, help_text="发送地址")
    confirmation_count = models.PositiveIntegerField(default=0, help_text="确认次数")
    qr_code = models.ImageField(upload_to='payment_qrcodes/', blank=True, null=True, help_text="支付二维码")
    
    class Meta:
        verbose_name = "USDT支付详情"
        verbose_name_plural = "USDT支付详情"
        
    def __str__(self):
        return f"USDT - {self.payment.id}"


class PayPalPaymentDetail(models.Model):
    """PayPal支付详情"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='paypal_details', help_text="关联的支付记录")
    paypal_order_id = models.CharField(max_length=255, blank=True, null=True, help_text="PayPal订单ID")
    paypal_payer_id = models.CharField(max_length=255, blank=True, null=True, help_text="PayPal付款人ID")
    payment_link = models.URLField(blank=True, null=True, help_text="支付链接")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="手续费")
    
    class Meta:
        verbose_name = "PayPal支付详情"
        verbose_name_plural = "PayPal支付详情"
        
    def __str__(self):
        return f"PayPal - {self.payment.id}"


class CreditCardPaymentDetail(models.Model):
    """信用卡支付详情"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='credit_card_details', help_text="关联的支付记录")
    processor = models.CharField(max_length=50, default='stripe', help_text="处理器")
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text="交易ID")
    card_type = models.CharField(max_length=50, blank=True, null=True, help_text="卡类型")
    last_four = models.CharField(max_length=4, blank=True, null=True, help_text="卡号后四位")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="手续费")
    
    class Meta:
        verbose_name = "信用卡支付详情"
        verbose_name_plural = "信用卡支付详情"
        
    def __str__(self):
        return f"信用卡 - {self.payment.id}"


class PaymentWebhookLog(models.Model):
    """支付Webhook日志"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, help_text="事件类型")
    payload = models.JSONField(default=dict, help_text="原始请求数据")
    response = models.JSONField(default=dict, help_text="响应数据")
    status = models.CharField(max_length=20, default='pending', help_text="处理状态")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Webhook日志"
        verbose_name_plural = "Webhook日志"
        
    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
