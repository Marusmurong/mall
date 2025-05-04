from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from payment.models import Payment, PaymentMethod, USDTPaymentDetail, PayPalPaymentDetail
from .serializers import (
    PaymentSerializer, PaymentMethodSerializer, 
    PaymentCreateSerializer, PaymentVerifySerializer,
    USDTPaymentDetailSerializer, PayPalPaymentDetailSerializer
)
from api.exceptions import BusinessException

class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    支付方式API视图集
    提供支付方式的只读查询功能
    """
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]


class PaymentViewSet(viewsets.ModelViewSet):
    """
    支付记录API视图集
    提供支付的创建和查询功能
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """获取当前用户的支付记录"""
        user = self.request.user
        
        # 如果用户登录，返回与用户相关的支付记录
        if user.is_authenticated:
            # 包括 用户作为付款人的记录 以及 用户的心愿单物品相关的支付记录
            return Payment.objects.filter(
                Q(payer=user) | Q(wishlist_item__wishlist__user=user)
            ).select_related('payment_method')
            
        # 对于匿名用户，如果是创建支付的操作，允许操作
        if self.action == 'create':
            return Payment.objects.none()
            
        # 如果是查询操作，返回空结果集
        return Payment.objects.none()
    
    def get_serializer_class(self):
        """根据不同的操作返回不同的序列化器"""
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'verify_payment':
            return PaymentVerifySerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        """创建支付记录"""
        payment = serializer.save()
        
        # 获取序列化结果中的数据标记已经处理完成
        serializer.instance = payment
    
    def create(self, request, *args, **kwargs):
        """重写create方法，确保返回payment_link"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # 获取支付链接
        payment = serializer.instance
        payment_serializer = PaymentSerializer(payment)
        response_data = payment_serializer.data
        
        # 确保payment_link字段存在于响应中
        payment_link = None
        
        # 检查支付方式和相关支付详情
        if payment.payment_method.payment_type == 'paypal':
            try:
                if hasattr(payment, 'paypal_details') and payment.paypal_details and payment.paypal_details.payment_link:
                    payment_link = payment.paypal_details.payment_link
            except Exception as e:
                print(f"获取PayPal支付链接错误: {str(e)}")
        
        elif payment.payment_method.payment_type == 'coinbase_commerce' or payment.payment_method.code == 'coinbase_commerce':
            try:
                if hasattr(payment, 'coinbase_details') and payment.coinbase_details and payment.coinbase_details.hosted_url:
                    payment_link = payment.coinbase_details.hosted_url
                    print(f"获取到Coinbase支付链接: {payment_link}")
            except Exception as e:
                print(f"获取Coinbase支付链接错误: {str(e)}")
        
        # 从payment_data中获取
        if not payment_link and payment.payment_data:
            payment_link = payment.payment_data.get('checkout_url') or payment.payment_data.get('payment_link')
            print(f"从payment_data获取支付链接: {payment_link}")
        
        # 添加payment_link到响应中
        if payment_link:
            response_data['payment_link'] = payment_link
            print(f"返回支付链接到前端: {payment_link}")
        else:
            print("警告: 未找到支付链接，前端可能无法跳转")
        
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消支付"""
        payment = self.get_object()
        
        # 检查是否可以取消
        if payment.status not in ['pending', 'processing']:
            return Response(
                {"detail": "只有待处理或处理中的支付才能取消"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新支付状态
        payment.status = 'cancelled'
        payment.status_message = "用户取消了支付"
        payment.save()
        
        return Response(PaymentSerializer(payment).data)
    
    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        """验证支付结果"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment = serializer.context['payment']
        
        # 根据支付方式进行不同的验证逻辑
        if payment.payment_method.payment_type == 'usdt':
            # USDT验证逻辑
            try:
                transaction_hash = serializer.validated_data.get('transaction_hash')
                if not transaction_hash:
                    return Response(
                        {"detail": "USDT支付需要提供交易哈希"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 获取USDT支付详情
                usdt_detail = payment.usdt_details
                
                # 更新交易哈希
                usdt_detail.transaction_hash = transaction_hash
                usdt_detail.confirmation_count = 1  # 模拟确认次数
                usdt_detail.save()
                
                # 更新支付状态
                payment.status = 'processing'
                payment.status_message = "USDT交易已提交，等待确认"
                payment.save()
                
                # TODO: 实际项目中，这里应该调用异步任务去区块链上验证交易
                
                return Response({
                    "detail": "USDT交易已提交，等待确认",
                    "payment": PaymentSerializer(payment).data
                })
                
            except Exception as e:
                return Response(
                    {"detail": f"USDT交易验证失败: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        elif payment.payment_method.payment_type == 'paypal':
            # PayPal验证逻辑
            try:
                paypal_order_id = serializer.validated_data.get('paypal_order_id')
                if not paypal_order_id:
                    return Response(
                        {"detail": "PayPal支付需要提供订单ID"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 获取PayPal支付详情
                paypal_detail = payment.paypal_details
                
                # 更新PayPal订单ID
                paypal_detail.paypal_order_id = paypal_order_id
                paypal_detail.save()
                
                # 更新支付状态
                payment.status = 'completed'
                payment.status_message = "PayPal支付成功"
                payment.transaction_id = paypal_order_id
                payment.completed_at = timezone.now()
                payment.save()
                
                # 如果支付关联心愿单物品，更新心愿单物品状态
                if payment.wishlist_item:
                    payment.wishlist_item.purchased = True
                    payment.wishlist_item.purchased_at = timezone.now()
                    payment.wishlist_item.purchased_by = payment.payer
                    payment.wishlist_item.payment_status = 'paid'
                    payment.wishlist_item.payment_completed = True
                    payment.wishlist_item.current_payment = payment
                    payment.wishlist_item.save()
                
                # 如果支付关联订单，更新订单状态
                if payment.payment_data and 'order_id' in payment.payment_data:
                    from order.models import Order, OrderLog
                    try:
                        order_id = payment.payment_data['order_id']
                        order = Order.objects.get(id=order_id)
                        
                        # 更新订单状态
                        old_status = order.status
                        order.status = 'paid'
                        order.payment = payment
                        order.payment_method = payment.payment_method.name
                        order.payment_platform = 'PayPal'
                        order.external_order_id = paypal_order_id
                        order.transaction_id = paypal_order_id
                        order.payment_time = timezone.now()
                        order.payment_status = 'paid'
                        order.save()
                        
                        # 创建订单日志
                        OrderLog.objects.create(
                            order=order,
                            action="支付成功",
                            status_from=old_status,
                            status_to='paid',
                            is_system=True,
                            note=f"用户通过PayPal完成支付，交易ID: {paypal_order_id}"
                        )
                    except Order.DoesNotExist:
                        # 订单不存在，不影响支付结果
                        pass
                
                return Response({
                    "detail": "PayPal支付验证成功",
                    "payment": PaymentSerializer(payment).data
                })
                
            except Exception as e:
                return Response(
                    {"detail": f"PayPal交易验证失败: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        else:
            return Response(
                {"detail": f"不支持的支付方式验证: {payment.payment_method.payment_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def check_status(self, request, pk=None):
        """查询支付状态"""
        payment = self.get_object()
        
        # TODO: 实际项目中，这里应该查询第三方支付平台获取最新状态
        
        return Response({
            "status": payment.status,
            "status_message": payment.status_message,
            "payment": PaymentSerializer(payment).data
        })


class USDTPaymentDetailView(generics.RetrieveAPIView):
    """
    USDT支付详情API视图
    提供USDT支付详情的查询功能
    """
    serializer_class = USDTPaymentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """获取USDT支付详情"""
        payment_id = self.kwargs.get('payment_id')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            # 检查权限
            if payment.payer != self.request.user and payment.wishlist_item.wishlist.user != self.request.user:
                raise BusinessException("您没有权限查看此支付详情")
                
            # 获取USDT支付详情
            try:
                return payment.usdt_details
            except USDTPaymentDetail.DoesNotExist:
                raise BusinessException("USDT支付详情不存在")
                
        except Payment.DoesNotExist:
            raise BusinessException("支付记录不存在")


class PayPalPaymentDetailView(generics.RetrieveAPIView):
    """
    PayPal支付详情API视图
    提供PayPal支付详情的查询功能
    """
    serializer_class = PayPalPaymentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """获取PayPal支付详情"""
        payment_id = self.kwargs.get('payment_id')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            # 检查权限
            if payment.payer != self.request.user and payment.wishlist_item.wishlist.user != self.request.user:
                raise BusinessException("您没有权限查看此支付详情")
                
            # 获取PayPal支付详情
            try:
                return payment.paypal_details
            except PayPalPaymentDetail.DoesNotExist:
                raise BusinessException("PayPal支付详情不存在")
                
        except Payment.DoesNotExist:
            raise BusinessException("支付记录不存在")
