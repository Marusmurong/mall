from rest_framework import viewsets, generics, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
import logging
from .serializers import UserSerializer, UserRegisterSerializer, ShippingAddressSerializer
from users.models import ShippingAddress
from api.exceptions import BusinessException

User = get_user_model()
logger = logging.getLogger(__name__)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户个人信息API
    GET: 获取当前用户信息
    PUT/PATCH: 更新用户信息
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
        
    def update(self, request, *args, **kwargs):
        # 仅允许修改部分字段
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 不允许修改用户名
        serializer.validated_data.pop('username', None)
        
        self.perform_update(serializer)
        return Response(serializer.data)


class UserRegisterView(generics.CreateAPIView):
    """
    用户注册API
    POST: 创建新用户
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                user = serializer.save()
                
                # 生成JWT令牌
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            logger.warning(f"注册验证错误: {str(e)}")
            return Response({
                "code": 1,
                "message": e.detail,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"注册过程中出现错误: {str(e)}")
            return Response({
                "code": 1,
                "message": str(e),
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShippingAddressViewSet(viewsets.ModelViewSet):
    """
    收货地址API
    提供收货地址的增删改查功能
    """
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的收货地址"""
        return ShippingAddress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """获取默认收货地址"""
        default_address = self.get_queryset().filter(is_default=True).first()
        if not default_address:
            # 如果没有默认地址，返回第一个地址
            default_address = self.get_queryset().first()
            
        if not default_address:
            return Response({'detail': '没有收货地址'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(default_address)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置为默认收货地址"""
        address = self.get_object()
        
        # 将其他地址设为非默认
        self.get_queryset().exclude(id=address.id).update(is_default=False)
        
        # 设置当前地址为默认
        address.is_default = True
        address.save()
        
        serializer = self.get_serializer(address)
        return Response(serializer.data)
