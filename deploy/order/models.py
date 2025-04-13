import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

from payment.models import Payment
from wishlist_new.models import WishlistItem
from users.models import ShippingAddress

User = get_user_model()

# 订单状态选项
ORDER_STATUS_CHOICES = [
    ('pending', _('待处理')),
    ('paid', _('已支付')),
    ('processing', _('处理中')),
    ('shipped', _('已发货')),
    ('delivered', _('已送达')),
    ('completed', _('已完成')),
    ('cancelled', _('已取消')),
    ('refunding', _('退款中')),
    ('refunded', _('已退款')),
]

# 退款状态选项
REFUND_STATUS_CHOICES = [
    ('pending', _('待处理')),
    ('processing', _('处理中')),
    ('approved', _('已批准')),
    ('rejected', _('已拒绝')),
    ('completed', _('已完成')),
]


class Order(models.Model):
    """订单模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, verbose_name=_('订单号'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name=_('心愿单所有者'))
    wishlist_item = models.ForeignKey(WishlistItem, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name=_('心愿单物品'))
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name=_('支付记录'))
    
    # 订单基本信息
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('订单总额'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('货币'))
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name=_('订单状态'))
    
    # 付款人信息（匿名付款者）
    is_anonymous_payer = models.BooleanField(default=False, verbose_name=_('匿名付款'))
    payer_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('付款人姓名'))
    payer_email = models.EmailField(blank=True, null=True, verbose_name=_('付款人邮箱'))
    payer_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('付款人电话'))
    payer_message = models.TextField(blank=True, null=True, verbose_name=_('付款人留言'))
    
    # 支付详细信息（记录支付对账信息）
    payment_method = models.CharField(max_length=50, blank=True, verbose_name=_('支付方式'))
    payment_platform = models.CharField(max_length=50, blank=True, verbose_name=_('支付平台'))
    external_order_id = models.CharField(max_length=100, blank=True, verbose_name=_('外部订单号'))
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name=_('交易号/流水号'))
    payment_account = models.CharField(max_length=100, blank=True, verbose_name=_('支付账号'))
    payment_time = models.DateTimeField(null=True, blank=True, verbose_name=_('支付时间'))
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True, verbose_name=_('支付凭证'))
    payment_status = models.CharField(max_length=30, blank=True, verbose_name=_('支付状态'))
    payment_notes = models.TextField(blank=True, verbose_name=_('支付备注'))
    
    # 收货信息
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, verbose_name=_('收货地址'))
    recipient_name = models.CharField(max_length=100, verbose_name=_('收件人姓名'))
    recipient_phone = models.CharField(max_length=20, verbose_name=_('收件人电话'))
    shipping_address_text = models.TextField(verbose_name=_('收货地址文本'))
    
    # 发货信息
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name=_('物流单号'))
    shipping_carrier = models.CharField(max_length=50, blank=True, verbose_name=_('物流公司'))
    shipping_method = models.CharField(max_length=50, blank=True, verbose_name=_('配送方式'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('运费'))
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('发货时间'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('送达时间'))
    
    # 退款信息
    is_refunding = models.BooleanField(default=False, verbose_name=_('是否申请退款'))
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, blank=True, verbose_name=_('退款状态'))
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('退款金额'))
    refund_reason = models.TextField(blank=True, verbose_name=_('退款原因'))
    refunded_at = models.DateTimeField(null=True, blank=True, verbose_name=_('退款时间'))
    
    # 备注
    customer_notes = models.TextField(blank=True, verbose_name=_('客户备注'))
    admin_notes = models.TextField(blank=True, verbose_name=_('管理员备注'))
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('完成时间'))
    
    class Meta:
        verbose_name = _('订单')
        verbose_name_plural = _('订单')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"订单 {self.order_number}"
    
    def save(self, *args, **kwargs):
        # 如果没有订单号，则生成一个基于时间的唯一订单号
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # 如果订单完成，记录完成时间
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
            
        # 复制收货地址信息，防止原地址被删除或修改
        if self.shipping_address and not self.shipping_address_text:
            self.recipient_name = self.shipping_address.recipient_name
            self.recipient_phone = self.shipping_address.phone
            self.shipping_address_text = self.shipping_address.get_full_address()
        
        # 从支付记录同步支付信息
        if self.payment:
            # 同步交易ID和支付状态
            if not self.transaction_id and self.payment.transaction_id:
                self.transaction_id = self.payment.transaction_id
            
            if not self.payment_status:
                self.payment_status = self.payment.status
                
            if not self.payment_time and self.payment.completed_at:
                self.payment_time = self.payment.completed_at
            
            # 获取支付方式信息
            if hasattr(self.payment, 'payment_method') and self.payment.payment_method:
                if not self.payment_method:
                    self.payment_method = self.payment.payment_method.name
                
                if not self.payment_platform and self.payment.payment_method.payment_type:
                    self.payment_platform = self.payment.payment_method.payment_type
            
            # 同步付款人信息
            if self.payment.is_anonymous and not self.is_anonymous_payer:
                self.is_anonymous_payer = True
                
            if not self.payer_name and self.payment.payer_name:
                self.payer_name = self.payment.payer_name
                
            if not self.payer_email and self.payment.payer_email:
                self.payer_email = self.payment.payer_email
            
            # 提取支付数据中可能包含的外部订单号
            if not self.external_order_id and hasattr(self.payment, 'payment_data'):
                payment_data = self.payment.payment_data
                
                # 从不同支付方式中提取外部订单号
                if self.payment_platform == 'paypal' and 'paypal_order_id' in payment_data:
                    self.external_order_id = payment_data.get('paypal_order_id')
                elif self.payment_platform == 'usdt' and 'transaction_hash' in payment_data:
                    self.external_order_id = payment_data.get('transaction_hash')
                elif 'order_id' in payment_data:
                    self.external_order_id = payment_data.get('order_id')
                    
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """生成订单号"""
        import random
        prefix = timezone.now().strftime('%Y%m%d')
        suffix = ''.join(random.choices('0123456789', k=8))
        return f"{prefix}{suffix}"
    
    def mark_as_paid(self):
        """标记为已支付"""
        self.status = 'paid'
        self.save(update_fields=['status', 'updated_at'])
        return True
    
    def mark_as_shipped(self, tracking_number='', shipping_carrier=''):
        """标记为已发货"""
        self.status = 'shipped'
        self.tracking_number = tracking_number
        self.shipping_carrier = shipping_carrier
        self.shipped_at = timezone.now()
        self.save(update_fields=['status', 'tracking_number', 'shipping_carrier', 'shipped_at', 'updated_at'])
        return True
    
    def mark_as_delivered(self):
        """标记为已送达"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])
        return True
    
    def mark_as_completed(self):
        """标记为已完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
        return True
    
    def cancel(self, reason=''):
        """取消订单"""
        self.status = 'cancelled'
        if reason:
            self.admin_notes += f"\n取消原因: {reason}"
        self.save(update_fields=['status', 'admin_notes', 'updated_at'])
        return True
    
    def request_refund(self, amount, reason=''):
        """申请退款"""
        self.is_refunding = True
        self.refund_status = 'pending'
        self.refund_amount = amount
        self.refund_reason = reason
        self.status = 'refunding'
        self.save(update_fields=['is_refunding', 'refund_status', 'refund_amount', 'refund_reason', 'status', 'updated_at'])
        return True
    
    def process_refund(self):
        """处理退款"""
        self.refund_status = 'processing'
        self.save(update_fields=['refund_status', 'updated_at'])
        return True
    
    def approve_refund(self):
        """批准退款"""
        self.refund_status = 'approved'
        self.save(update_fields=['refund_status', 'updated_at'])
        return True
    
    def complete_refund(self):
        """完成退款"""
        self.refund_status = 'completed'
        self.status = 'refunded'
        self.refunded_at = timezone.now()
        self.save(update_fields=['refund_status', 'status', 'refunded_at', 'updated_at'])
        return True
    
    def reject_refund(self, reason=''):
        """拒绝退款"""
        self.refund_status = 'rejected'
        self.is_refunding = False
        self.status = self.prev_status if hasattr(self, 'prev_status') else 'paid'
        if reason:
            self.admin_notes += f"\n拒绝退款原因: {reason}"
        self.save(update_fields=['refund_status', 'is_refunding', 'status', 'admin_notes', 'updated_at'])
        return True
    
    def get_order_status_display_html(self):
        """获取订单状态HTML显示"""
        status_colors = {
            'pending': 'secondary',
            'paid': 'info',
            'processing': 'primary',
            'shipped': 'primary',
            'delivered': 'success',
            'completed': 'success',
            'cancelled': 'danger',
            'refunding': 'warning',
            'refunded': 'dark',
        }
        color = status_colors.get(self.status, 'secondary')
        return f'<span class="badge badge-{color}">{self.get_status_display()}</span>'


class OrderLog(models.Model):
    """订单日志"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs', verbose_name=_('订单'))
    action = models.CharField(max_length=50, verbose_name=_('操作'))
    status_from = models.CharField(max_length=20, blank=True, verbose_name=_('原状态'))
    status_to = models.CharField(max_length=20, blank=True, verbose_name=_('新状态'))
    data = models.JSONField(default=dict, blank=True, verbose_name=_('数据'))
    note = models.TextField(blank=True, verbose_name=_('备注'))
    
    # 操作人信息
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operation_logs', verbose_name=_('操作人'))
    is_system = models.BooleanField(default=False, verbose_name=_('是否系统操作'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP地址'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    
    class Meta:
        verbose_name = _('订单日志')
        verbose_name_plural = _('订单日志')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.order.order_number} - {self.action} - {self.created_at}"


class RefundDetail(models.Model):
    """退款详情模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refund_details', verbose_name=_('订单'))
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, related_name='refund_details', verbose_name=_('原支付记录'))
    
    # 退款基本信息
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('退款金额'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('货币'))
    refund_method = models.CharField(max_length=50, verbose_name=_('退款方式'))
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending', verbose_name=_('状态'))
    
    # 退款原因和说明
    reason = models.CharField(max_length=100, verbose_name=_('退款原因'))
    description = models.TextField(blank=True, verbose_name=_('详细说明'))
    
    # 退款记录信息
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name=_('交易ID'))
    refund_data = models.JSONField(default=dict, blank=True, verbose_name=_('退款数据'))
    admin_notes = models.TextField(blank=True, verbose_name=_('管理员备注'))
    
    # 处理退款的管理员
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds', verbose_name=_('处理人'))
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('处理时间'))
    
    # 退款凭证
    receipt_image = models.ImageField(upload_to='refund_receipts/', blank=True, null=True, verbose_name=_('退款凭证'))
    
    # 时间字段
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name=_('申请时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('完成时间'))
    
    class Meta:
        verbose_name = _('退款详情')
        verbose_name_plural = _('退款详情')
        ordering = ['-requested_at']
        
    def __str__(self):
        return f"{self.order.order_number} - {self.refund_amount}{self.currency} - {self.get_status_display()}"
    
    def mark_as_processed(self, user=None):
        """标记为已处理"""
        self.status = 'processing'
        self.processed_by = user
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_by', 'processed_at', 'updated_at'])
        return True
    
    def mark_as_completed(self, transaction_id=None):
        """标记为已完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save(update_fields=['status', 'completed_at', 'transaction_id', 'updated_at'])
        return True
    
    def mark_as_rejected(self, reason=None):
        """标记为已拒绝"""
        self.status = 'rejected'
        if reason:
            self.admin_notes += f"\n拒绝原因: {reason}"
        self.save(update_fields=['status', 'admin_notes', 'updated_at'])
        return True
