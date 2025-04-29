from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import UserSerializer, UserRegisterSerializer, ShippingAddressSerializer
from users.models import ShippingAddress
from api.exceptions import BusinessException
from rest_framework.views import APIView

User = get_user_model()

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


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


class TelegramTokenView(APIView):
    """
    生成Telegram连接令牌
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 生成一个随机的token，包含用户ID信息以便于后续验证
        import uuid
        import hashlib
        import time
        from django.utils import timezone
        
        user = request.user
        # 创建一个唯一的token，包含用户ID和时间戳
        token_base = f"{user.id}:{uuid.uuid4()}:{int(time.time())}"
        # 使用SHA-256哈希算法生成token
        token = hashlib.sha256(token_base.encode()).hexdigest()[:32]
        
        # 将token保存到用户模型中，以便后续验证
        # 使用UserProfile模型存储Telegram相关信息
        profile = user.profile
        profile.telegram_token = token
        profile.telegram_token_created_at = timezone.now()
        profile.save()
        
        # 返回标准格式的响应
        return Response({
            "code": 0,
            "message": "成功生成Telegram绑定令牌",
            "data": {
                "token": token,
                "expires_in": 3600  # 令牌有效期1小时
            }
        })


class TelegramBindView(APIView):
    """
    处理Telegram绑定请求
    此API由Telegram机器人调用，用于验证用户提供的token并完成绑定
    """
    permission_classes = [permissions.AllowAny]  # Telegram机器人调用，不需要认证
    
    def post(self, request):
        from django.utils import timezone
        from datetime import timedelta
        
        token = request.data.get('token')
        telegram_username = request.data.get('username')
        telegram_chat_id = request.data.get('chat_id')
        
        if not all([token, telegram_username, telegram_chat_id]):
            return Response({
                "code": 400,
                "message": "缺少必要参数"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找拥有此token的用户
        from users.models import UserProfile
        try:
            profile = UserProfile.objects.get(telegram_token=token)
            
            # 检查token是否过期（1小时有效期）
            if profile.telegram_token_created_at:
                token_age = timezone.now() - profile.telegram_token_created_at
                if token_age > timedelta(hours=1):
                    return Response({
                        "code": 400,
                        "message": "令牌已过期，请重新生成"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 完成绑定
            profile.telegram_connected = True
            profile.telegram_username = telegram_username
            profile.telegram_chat_id = telegram_chat_id
            # 清除token，防止重复使用
            profile.telegram_token = ''
            profile.save()
            
            return Response({
                "code": 0,
                "message": "Telegram绑定成功",
                "data": {
                    "username": profile.user.username,
                    "email": profile.user.email
                }
            })
            
        except UserProfile.DoesNotExist:
            return Response({
                "code": 404,
                "message": "无效的令牌"
            }, status=status.HTTP_404_NOT_FOUND)


class TelegramStatusView(APIView):
    """
    获取Telegram连接状态
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        # 检查用户是否已绑定Telegram
        profile = user.profile
        telegram_connected = profile.telegram_connected
        telegram_username = profile.telegram_username if telegram_connected else ''
        
        return Response({
            "code": 0,
            "message": "成功获取Telegram绑定状态",
            "data": {
                "connected": telegram_connected,
                "username": telegram_username
            }
        })


class TelegramDisconnectView(APIView):
    """
    断开Telegram连接
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        # 清除用户的Telegram绑定信息
        profile = user.profile
        profile.telegram_connected = False
        profile.telegram_username = ''
        profile.telegram_chat_id = ''
        profile.telegram_token = ''
        profile.telegram_token_created_at = None
        profile.save()
        
        return Response({
            "code": 0,
            "message": "成功解除Telegram绑定"
        })
