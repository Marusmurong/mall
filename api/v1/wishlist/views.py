from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, F, Case, When, Value, IntegerField, DecimalField
from django.utils import timezone
from wishlist_new.models import Wishlist, WishlistItem, WishlistView
from .serializers import WishlistSerializer, WishlistItemSerializer, WishlistItemCreateSerializer
from api.exceptions import BusinessException

class WishlistViewSet(viewsets.ModelViewSet):
    """
    心愿单API视图集
    提供个人心愿单的增删改查功能，以及统计功能
    """
    serializer_class = WishlistSerializer
    
    def get_permissions(self):
        """
        根据操作设置权限
        - 查看公开心愿单允许匿名访问
        - 修改心愿单需要用户认证
        - 记录浏览量允许匿名访问
        """
        if self.action in ['retrieve_by_share_code', 'list_public', 'view', 'stats', 'share_link']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        获取当前用户的心愿单
        """
        # 默认只返回当前用户的心愿单
        if self.request.user.is_authenticated:
            return Wishlist.objects.filter(user=self.request.user)
        # 未登录用户返回空查询集
        return Wishlist.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        """
        查看心愿单详情
        - 支持查看自己的心愿单
        - 支持查看公开的心愿单
        """
        instance = self.get_object()
        
        # 检查权限：只能查看自己的心愿单或公开的心愿单
        if not instance.is_public and instance.user != request.user:
            return Response(
                {"detail": "您没有权限查看此心愿单"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        获取当前用户的心愿单
        如果没有则创建一个新的心愿单
        如果有多个，则返回第一个
        """
        # 获取用户的所有心愿单
        wishlists = Wishlist.objects.filter(user=request.user)
        
        # 检查是否有心愿单
        if wishlists.exists():
            # 如果有多个心愿单，返回第一个
            wishlist = wishlists.first()
            # 记录日志
            if wishlists.count() > 1:
                print(f"用户 {request.user.username} 有多个心愿单，返回第一个（ID: {wishlist.id}）")
        else:
            # 如果没有，创建一个新的
            wishlist = Wishlist.objects.create(
                user=request.user,
                name=f'{request.user.username}的心愿单'
            )
            print(f"为用户 {request.user.username} 创建了新的心愿单（ID: {wishlist.id}）")
        
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='share/(?P<share_code>[^/.]+)')
    def retrieve_by_share_code(self, request, share_code=None):
        """
        通过分享码查看心愿单
        允许匿名访问，但只能查看公开的心愿单
        """
        try:
            wishlist = Wishlist.objects.get(share_code=share_code, is_public=True)
        except Wishlist.DoesNotExist:
            return Response(
                {"detail": "心愿单不存在或不是公开的"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def list_public(self, request):
        """
        列出公开的心愿单
        支持分页查询
        """
        # 查询公开的心愿单
        public_wishlists = Wishlist.objects.filter(is_public=True)
        
        # 支持按用户名搜索
        username = request.query_params.get('username', None)
        if username:
            public_wishlists = public_wishlists.filter(user__username__icontains=username)
            
        # 分页处理
        page = self.paginate_queryset(public_wishlists)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(public_wishlists, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """
        记录心愿单浏览量
        每次访问心愿单页面时调用
        """
        try:
            wishlist = self.get_object()
        except Exception:
            return Response({"detail": "心愿单不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 记录浏览信息
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user = request.user if request.user.is_authenticated else None
        
        # 创建浏览记录
        WishlistView.objects.create(
            wishlist=wishlist,
            ip_address=ip_address,
            user_agent=user_agent,
            user=user
        )
        
        return Response({"success": True, "views": WishlistView.objects.filter(wishlist=wishlist).count()})
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        获取心愿单统计数据
        包括浏览量、已购买商品数量和金额、未购买商品数量和金额
        """
        try:
            wishlist = self.get_object()
        except Exception:
            return Response({"detail": "心愿单不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 获取浏览量
        views_count = WishlistView.objects.filter(wishlist=wishlist).count()
        
        # 获取商品统计
        items = WishlistItem.objects.filter(wishlist=wishlist)
        
        # 已购买商品统计
        purchased_items = items.filter(purchased=True)
        purchased_count = purchased_items.count()
        purchased_amount = purchased_items.aggregate(total=Sum('price'))['total'] or 0
        
        # 未购买商品统计
        unpurchased_items = items.filter(purchased=False)
        unpurchased_count = unpurchased_items.count()
        unpurchased_amount = unpurchased_items.aggregate(total=Sum('price'))['total'] or 0
        
        # 支付完成的商品统计
        payment_completed_items = items.filter(payment_completed=True)
        payment_completed_count = payment_completed_items.count()
        payment_completed_amount = payment_completed_items.aggregate(total=Sum('price'))['total'] or 0
        
        return Response({
            "views_count": views_count,
            "purchased": {
                "count": purchased_count,
                "amount": purchased_amount
            },
            "unpurchased": {
                "count": unpurchased_count,
                "amount": unpurchased_amount
            },
            "payment_completed": {
                "count": payment_completed_count,
                "amount": payment_completed_amount
            }
        })
    
    @action(detail=False, methods=['get'])
    def stats_all(self, request):
        """
        获取所有心愿单的汇总统计数据
        仅限已登录用户查看自己的心愿单统计
        """
        if not request.user.is_authenticated:
            return Response({"detail": "需要登录"}, status=status.HTTP_401_UNAUTHORIZED)
            
        # 获取用户的所有心愿单
        wishlists = Wishlist.objects.filter(user=request.user)
        
        # 获取总浏览量
        views_count = WishlistView.objects.filter(wishlist__in=wishlists).count()
        
        # 获取所有心愿单商品
        items = WishlistItem.objects.filter(wishlist__in=wishlists)
        
        # 已购买商品统计
        purchased_items = items.filter(purchased=True)
        purchased_count = purchased_items.count()
        purchased_amount = purchased_items.aggregate(total=Sum('price'))['total'] or 0
        
        # 未购买商品统计
        unpurchased_items = items.filter(purchased=False)
        unpurchased_count = unpurchased_items.count()
        unpurchased_amount = unpurchased_items.aggregate(total=Sum('price'))['total'] or 0
        
        # 支付完成的商品统计
        payment_completed_items = items.filter(payment_completed=True)
        payment_completed_count = payment_completed_items.count()
        payment_completed_amount = payment_completed_items.aggregate(total=Sum('price'))['total'] or 0
        
        return Response({
            "wishlists_count": wishlists.count(),
            "views_count": views_count,
            "purchased": {
                "count": purchased_count,
                "amount": purchased_amount
            },
            "unpurchased": {
                "count": unpurchased_count,
                "amount": unpurchased_amount
            },
            "payment_completed": {
                "count": payment_completed_count,
                "amount": payment_completed_amount
            }
        })
    
    @action(detail=True, methods=['get'])
    def share_link(self, request, pk=None):
        """
        获取心愿单分享链接
        """
        try:
            wishlist = self.get_object()
        except Exception:
            return Response({"detail": "心愿单不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 确保心愿单有分享码
        if not wishlist.share_code:
            wishlist.share_code = wishlist.generate_share_code()
            wishlist.save()
            
        # 构建分享链接
        base_url = request.build_absolute_uri('/').rstrip('/')
        share_url = f"{base_url}/wishlist/share/{wishlist.share_code}/"
        
        return Response({
            "share_code": wishlist.share_code,
            "share_url": share_url,
            "is_public": wishlist.is_public
        })


class WishlistItemViewSet(viewsets.ModelViewSet):
    """
    心愿单物品API视图集
    提供心愿单物品的增删改查功能
    """
    serializer_class = WishlistItemSerializer
    
    def get_permissions(self):
        """根据操作设置权限"""
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        """根据操作选择不同的序列化器"""
        if self.action == 'create':
            return WishlistItemCreateSerializer
        return WishlistItemSerializer
    
    def get_queryset(self):
        """获取当前用户心愿单中的物品"""
        if not self.request.user.is_authenticated:
            return WishlistItem.objects.none()
            
        # 获取当前用户的所有心愿单
        user_wishlists = Wishlist.objects.filter(user=self.request.user)
        
        # 返回这些心愿单中的所有物品
        return WishlistItem.objects.filter(wishlist__in=user_wishlists)
    
    def perform_create(self, serializer):
        """创建心愿单物品"""
        serializer.save()
    
    def perform_update(self, serializer):
        """更新心愿单物品"""
        # 检查权限：只能修改自己心愿单中的物品
        item = self.get_object()
        if item.wishlist.user != self.request.user:
            raise BusinessException("您没有权限修改此心愿单物品")
            
        serializer.save()
    
    def perform_destroy(self, instance):
        """删除心愿单物品"""
        # 检查权限：只能删除自己心愿单中的物品
        if instance.wishlist.user != self.request.user:
            raise BusinessException("您没有权限删除此心愿单物品")
            
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """
        标记心愿单物品为已购买
        可由用户自己或其他人操作
        """
        item = self.get_object()
        
        # 如果已购买，则返回错误
        if item.purchased:
            return Response(
                {"detail": "此物品已被购买"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 标记为已购买
        item.purchased = True
        item.purchased_by = request.user
        item.purchased_at = timezone.now()
        item.save()
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def user_items(self, request):
        """
        获取用户的所有心愿单商品
        """
        if not request.user.is_authenticated:
            return Response({"detail": "需要登录"}, status=status.HTTP_401_UNAUTHORIZED)
            
        # 获取用户的所有心愿单
        user_wishlists = Wishlist.objects.filter(user=request.user)
        
        # 获取这些心愿单中的所有商品
        items = WishlistItem.objects.filter(wishlist__in=user_wishlists)
        
        # 分页处理
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'], url_path='check-product/(?P<product_id>[^/.]+)')
    def check_product_in_wishlist(self, request, product_id=None):
        """
        检查商品是否已在用户的任何心愿单中
        """
        if not request.user.is_authenticated:
            return Response({"in_wishlist": False})
            
        # 获取用户的所有心愿单
        user_wishlists = Wishlist.objects.filter(user=request.user)
        
        # 检查商品是否在任何心愿单中
        in_wishlist = WishlistItem.objects.filter(
            wishlist__in=user_wishlists,
            product_id=product_id
        ).exists()
        
        # 如果在心愿单中，返回心愿单信息
        if in_wishlist:
            item = WishlistItem.objects.filter(
                wishlist__in=user_wishlists,
                product_id=product_id
            ).first()
            return Response({
                "in_wishlist": True,
                "wishlist_id": str(item.wishlist.id),
                "wishlist_name": item.wishlist.name,
                "item_id": str(item.id)
            })
            
        return Response({"in_wishlist": False})
