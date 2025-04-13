from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PaymentMethod, Payment, USDTPaymentDetail, 
    PayPalPaymentDetail, CreditCardPaymentDetail,
    PaymentWebhookLog
)
from .forms import PaymentMethodConfigForm

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    form = PaymentMethodConfigForm
    list_display = ('name', 'code', 'payment_type', 'is_active', 'test_mode', 'get_config_status')
    list_filter = ('payment_type', 'is_active', 'test_mode')
    search_fields = ('name', 'code')
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'payment_type', 'description', 'icon', 'is_active', 'test_mode')
        }),
        ('USDT支付配置', {
            'classes': ('collapse',),
            'fields': ('usdt_wallet_address', 'usdt_api_key', 'usdt_api_secret'),
        }),
        ('PayPal支付配置', {
            'classes': ('collapse',),
            'fields': ('paypal_client_id', 'paypal_client_secret', 'paypal_mode'),
        }),
        ('信用卡支付配置', {
            'classes': ('collapse',),
            'fields': ('cc_provider', 'cc_api_key', 'cc_api_secret'),
        }),
    )
    
    def get_config_status(self, obj):
        """检查支付方式配置状态"""
        if not obj.config:
            return format_html('<span style="color: red;">未配置</span>')
        
        if obj.payment_type == 'usdt' and obj.get_config('wallet_address'):
            return format_html('<span style="color: green;">已配置</span>')
        elif obj.payment_type == 'paypal' and obj.get_config('client_id') and obj.get_config('client_secret'):
            return format_html('<span style="color: green;">已配置</span>')
        elif obj.payment_type == 'credit_card' and obj.get_config('api_key') and obj.get_config('api_secret'):
            return format_html('<span style="color: green;">已配置</span>')
        else:
            return format_html('<span style="color: orange;">配置不完整</span>')
    
    get_config_status.short_description = '配置状态'
    
    def get_fieldsets(self, request, obj=None):
        """根据支付方式类型动态显示配置字段"""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            # 保留基本字段和对应支付方式的配置字段
            new_fieldsets = [fieldsets[0]]  # 保留基本字段
            
            if obj.payment_type == 'usdt':
                new_fieldsets.append(fieldsets[1])  # USDT配置
            elif obj.payment_type == 'paypal':
                new_fieldsets.append(fieldsets[2])  # PayPal配置
            elif obj.payment_type == 'credit_card':
                new_fieldsets.append(fieldsets[3])  # 信用卡配置
                
            return new_fieldsets
        return fieldsets


class USDTPaymentDetailInline(admin.StackedInline):
    model = USDTPaymentDetail
    can_delete = False
    extra = 0


class PayPalPaymentDetailInline(admin.StackedInline):
    model = PayPalPaymentDetail
    can_delete = False
    extra = 0


class CreditCardPaymentDetailInline(admin.StackedInline):
    model = CreditCardPaymentDetail
    can_delete = False
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_method', 'amount', 'currency', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'is_anonymous')
    search_fields = ('id', 'payer_email', 'payer_name', 'transaction_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'completed_at', 'payment_data', 'transaction_id')
    date_hierarchy = 'created_at'
    
    def get_inlines(self, request, obj=None):
        """根据支付方式动态添加内联"""
        if obj is None:
            return []
        
        inlines = []
        if obj.payment_method.payment_type == 'usdt':
            inlines.append(USDTPaymentDetailInline)
        elif obj.payment_method.payment_type == 'paypal':
            inlines.append(PayPalPaymentDetailInline)
        elif obj.payment_method.payment_type == 'credit_card':
            inlines.append(CreditCardPaymentDetailInline)
        
        return inlines
    
    def has_add_permission(self, request):
        # 暂时禁用添加功能，直到修复模型关联
        return False


@admin.register(PaymentWebhookLog)
class PaymentWebhookLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_type', 'status', 'created_at')
    list_filter = ('event_type', 'status', 'created_at')
    search_fields = ('id', 'event_type', 'payload')
    readonly_fields = ('id', 'created_at', 'payload', 'response')
