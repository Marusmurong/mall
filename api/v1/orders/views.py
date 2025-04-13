from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from order.models import Order, OrderItem, OrderLog, RefundDetail
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderItemSerializer,
    OrderLogSerializer, RefundDetailSerializer, RefundCreateSerializer
)
from api.exceptions import BusinessException
from api.middleware.site_middleware import get_current_site

class OrderViewSet(viewsets.ModelViewSet):
    """
    订单API视图集
    提供订单的增删改查功能
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的订单"""
        user = self.request.user
        queryset = Order.objects.filter(user=user)
        
        # 按状态筛选
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # 按创建时间排序（默认为降序）
        order_by = self.request.query_params.get('order_by', '-created_at')
        if order_by in ['created_at', '-created_at', 'updated_at', '-updated_at', 'total_amount', '-total_amount']:
            queryset = queryset.order_by(order_by)
            
        return queryset
    
    def get_serializer_class(self):
        """根据不同的操作使用不同的序列化器"""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        """创建订单"""
        serializer.save()
    
    def perform_update(self, serializer):
        """更新订单"""
        # 只有待处理状态的订单可以被用户修改
        instance = self.get_object()
        if instance.status != 'pending':
            raise BusinessException("只有待处理状态的订单可以被修改")
            
        serializer.save()
    
    def perform_destroy(self, instance):
        """删除订单"""
        # 只有pending状态的订单可以被取消
        if instance.status != 'pending':
            raise BusinessException("只有待处理状态的订单可以被取消")
            
        # 更新订单状态为取消
        instance.status = 'cancelled'
        instance.save()
        
        # 添加订单日志
        OrderLog.objects.create(
            order=instance,
            action="取消订单",
            status_from='pending',
            status_to='cancelled',
            user=self.request.user,
            note="用户取消了订单"
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        instance = self.get_object()
        
        # 只有待处理或支付状态的订单可以被取消
        if instance.status not in ['pending', 'paid', 'processing']:
            return Response({"detail": "当前状态的订单不能被取消"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 更新订单状态
        old_status = instance.status
        instance.status = 'cancelled'
        instance.save()
        
        # 添加订单日志
        OrderLog.objects.create(
            order=instance,
            action="取消订单",
            status_from=old_status,
            status_to='cancelled',
            user=request.user,
            note=request.data.get('reason', "用户取消了订单")
        )
        
        return Response(OrderSerializer(instance).data)
    
    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        """申请退款"""
        order = self.get_object()
        
        serializer = RefundCreateSerializer(
            data=request.data,
            context={'request': request, 'order': order}
        )
        serializer.is_valid(raise_exception=True)
        refund = serializer.save()
        
        return Response(RefundDetailSerializer(refund).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def confirm_receipt(self, request, pk=None):
        """确认收货"""
        instance = self.get_object()
        
        # 只有已发货状态的订单可以确认收货
        if instance.status != 'shipped':
            return Response({"detail": "只有已发货的订单可以确认收货"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 更新订单状态
        instance.status = 'delivered'
        instance.delivered_at = timezone.now()
        instance.save()
        
        # 添加订单日志
        OrderLog.objects.create(
            order=instance,
            action="确认收货",
            status_from='shipped',
            status_to='delivered',
            user=request.user,
            note="用户确认收货"
        )
        
        return Response(OrderSerializer(instance).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成订单"""
        instance = self.get_object()
        
        # 只有已送达的订单可以标记为完成
        if instance.status != 'delivered':
            return Response({"detail": "只有已送达的订单可以标记为完成"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 更新订单状态
        instance.status = 'completed'
        instance.completed_at = timezone.now()
        instance.save()
        
        # 添加订单日志
        OrderLog.objects.create(
            order=instance,
            action="完成订单",
            status_from='delivered',
            status_to='completed',
            user=request.user,
            note="用户确认完成订单"
        )
        
        return Response(OrderSerializer(instance).data)
        
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """获取订单日志"""
        order = self.get_object()
        logs = order.logs.all().order_by('-created_at')
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = OrderLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = OrderLogSerializer(logs, many=True)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    订单项API视图集
    提供只读的订单项查询功能
    """
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的订单项"""
        return OrderItem.objects.filter(order__user=self.request.user)
        

class RefundDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    退款详情API视图集
    提供只读的退款详情查询功能
    """
    serializer_class = RefundDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的退款详情"""
        return RefundDetail.objects.filter(order__user=self.request.user)
