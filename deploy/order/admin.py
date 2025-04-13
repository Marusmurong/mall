from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db import models
from django.forms import Textarea, TextInput

from .models import Order, OrderLog, RefundDetail


class OrderLogInline(admin.TabularInline):
    model = OrderLog
    extra = 0
    readonly_fields = ('action', 'status_from', 'status_to', 'user', 'is_system', 'created_at')
    fields = ('action', 'status_from', 'status_to', 'note', 'user', 'is_system', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class RefundDetailInline(admin.StackedInline):
    model = RefundDetail
    extra = 0
    readonly_fields = ('requested_at', 'processed_at', 'completed_at')
    fieldsets = (
        ('基本信息', {
            'fields': (('refund_amount', 'currency', 'refund_method'), 'status')
        }),
        ('退款原因', {
            'fields': ('reason', 'description')
        }),
        ('处理信息', {
            'fields': (('transaction_id', 'processed_by'), ('requested_at', 'processed_at', 'completed_at'), 'receipt_image', 'admin_notes')
        })
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'get_user', 'get_wishlist_item', 'total_amount', 'currency', 
                   'get_payer_info', 'payment_method', 'external_order_id', 'get_status_display', 'created_at')
    list_filter = ('status', 'is_anonymous_payer', 'payment_method', 'payment_platform', 'is_refunding', 'refund_status', 
                  'created_at', 'payment_time', 'shipped_at', 'delivered_at')
    search_fields = ('order_number', 'user__username', 'external_order_id', 'transaction_id', 
                    'payer_name', 'payer_email', 'payer_phone', 'recipient_name', 
                    'recipient_phone', 'tracking_number')
    readonly_fields = ('id', 'order_number', 'created_at', 'updated_at', 'completed_at', 
                      'shipped_at', 'delivered_at', 'refunded_at', 'payment_time')
    inlines = [RefundDetailInline, OrderLogInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': (('order_number', 'status'), ('user', 'wishlist_item'), 
                     ('total_amount', 'currency'), ('created_at', 'updated_at', 'completed_at'))
        }),
        ('付款人信息', {
            'fields': (('is_anonymous_payer', 'payer_name'), ('payer_email', 'payer_phone'), 'payer_message'),
            'classes': ('collapse',),
        }),
        ('支付信息', {
            'fields': (('payment', 'payment_method', 'payment_platform'), 
                     ('external_order_id', 'transaction_id', 'payment_time'), 
                     ('payment_account', 'payment_status', 'payment_proof'), 'payment_notes')
        }),
        ('收货信息', {
            'fields': (('recipient_name', 'recipient_phone'), 'shipping_address', 'shipping_address_text')
        }),
        ('发货信息', {
            'fields': (('tracking_number', 'shipping_carrier', 'shipping_method'), 
                     ('shipping_cost', 'shipped_at', 'delivered_at'))
        }),
        ('退款信息', {
            'fields': (('is_refunding', 'refund_status'), ('refund_amount', 'refund_reason', 'refunded_at'))
        }),
        ('备注', {
            'fields': ('customer_notes', 'admin_notes')
        })
    )
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    }
    
    def get_status_display(self, obj):
        return mark_safe(obj.get_order_status_display_html())
    get_status_display.short_description = '状态'
    
    def get_user(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    get_user.short_description = '心愿单所有者'
    
    def get_payer_info(self, obj):
        if obj.is_anonymous_payer:
            info = "匿名: "
        else:
            info = ""
            
        if obj.payer_name:
            info += obj.payer_name
        elif obj.payer_email:
            info += obj.payer_email
        elif obj.payer_phone:
            info += obj.payer_phone
        else:
            return "-"
            
        return info
    get_payer_info.short_description = '付款人'
    
    def get_wishlist_item(self, obj):
        if obj.wishlist_item:
            url = reverse('admin:wishlist_new_wishlistitem_change', args=[obj.wishlist_item.id])
            return format_html('<a href="{}">{}</a>', url, obj.wishlist_item.title)
        return '-'
    get_wishlist_item.short_description = '心愿单物品'
    
    def save_model(self, request, obj, form, change):
        """保存模型时记录操作日志"""
        creating = not change
        old_status = None
        
        if not creating:
            # 获取修改前的状态
            old_obj = self.model.objects.get(pk=obj.pk)
            old_status = old_obj.status
        
        # 保存对象
        super().save_model(request, obj, form, change)
        
        # 记录日志
        if creating:
            # 创建订单日志
            OrderLog.objects.create(
                order=obj,
                action='create',
                status_to=obj.status,
                user=request.user,
                note='订单创建'
            )
        elif old_status != obj.status:
            # 状态变更日志
            OrderLog.objects.create(
                order=obj,
                action='status_change',
                status_from=old_status,
                status_to=obj.status,
                user=request.user,
                note=f'状态从 {old_status} 变更为 {obj.status}'
            )


@admin.register(OrderLog)
class OrderLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'action', 'status_from', 'status_to', 'user', 'is_system', 'created_at')
    list_filter = ('action', 'is_system', 'created_at')
    search_fields = ('order__order_number', 'note', 'user__username')
    readonly_fields = ('order', 'action', 'status_from', 'status_to', 'data', 'user', 'is_system', 'ip_address', 'created_at')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RefundDetail)
class RefundDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'refund_amount', 'currency', 'refund_method', 'reason', 'status', 'processed_by', 'requested_at', 'completed_at')
    list_filter = ('status', 'refund_method', 'requested_at')
    search_fields = ('order__order_number', 'reason', 'description', 'admin_notes')
    readonly_fields = ('requested_at', 'updated_at', 'completed_at')
    date_hierarchy = 'requested_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': (('order', 'payment'), ('refund_amount', 'currency', 'refund_method'), 'status')
        }),
        ('退款原因', {
            'fields': ('reason', 'description')
        }),
        ('处理信息', {
            'fields': (('transaction_id', 'processed_by', 'processed_at'), ('requested_at', 'updated_at', 'completed_at'), 'receipt_image', 'refund_data', 'admin_notes')
        })
    )
    
    def save_model(self, request, obj, form, change):
        """保存模型时更新相关订单状态"""
        creating = not change
        old_status = None
        
        if not creating:
            # 获取修改前的状态
            old_obj = self.model.objects.get(pk=obj.pk)
            old_status = old_obj.status
        
        # 保存对象
        super().save_model(request, obj, form, change)
        
        # 更新订单状态
        if old_status != obj.status:
            order = obj.order
            
            if obj.status == 'completed':
                # 退款完成
                order.status = 'refunded'
                order.refund_status = 'completed'
                order.refunded_at = obj.completed_at
                order.save(update_fields=['status', 'refund_status', 'refunded_at'])
                
                # 记录订单日志
                OrderLog.objects.create(
                    order=order,
                    action='refund_completed',
                    status_from=old_status,
                    status_to='refunded',
                    user=request.user,
                    note=f'退款完成: {obj.refund_amount}{obj.currency}'
                )
            elif obj.status == 'rejected':
                # 退款被拒绝
                order.refund_status = 'rejected'
                order.is_refunding = False
                
                # 恢复之前的订单状态
                if order.status == 'refunding':
                    order.status = 'paid'  # 默认恢复到已支付状态
                
                order.save(update_fields=['status', 'refund_status', 'is_refunding'])
                
                # 记录订单日志
                OrderLog.objects.create(
                    order=order,
                    action='refund_rejected',
                    status_to=order.status,
                    user=request.user,
                    note=f'退款被拒绝: {obj.admin_notes}'
                )
            elif obj.status == 'processing':
                # 退款处理中
                order.refund_status = 'processing'
                order.save(update_fields=['refund_status'])
                
                # 记录订单日志
                OrderLog.objects.create(
                    order=order,
                    action='refund_processing',
                    user=request.user,
                    note='退款处理中'
                )
