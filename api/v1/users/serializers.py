from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from users.models import ShippingAddress
from django.db.models import Q

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class ShippingAddressSerializer(serializers.ModelSerializer):
    """收货地址序列化器"""
    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'user', 'name', 'phone', 'province', 'city', 
            'district', 'address', 'zip_code', 'is_default'
        ]
        read_only_fields = ['id', 'user']
        
    def create(self, validated_data):
        """创建收货地址，如果是默认地址则将其他地址设为非默认"""
        user = self.context['request'].user
        validated_data['user'] = user
        
        # 如果设置为默认地址，则将该用户的其他地址设为非默认
        if validated_data.get('is_default', False):
            ShippingAddress.objects.filter(user=user).update(is_default=False)
            
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """更新收货地址，如果是默认地址则将其他地址设为非默认"""
        # 如果设置为默认地址，则将该用户的其他地址设为非默认
        if validated_data.get('is_default', False) and not instance.is_default:
            ShippingAddress.objects.filter(user=instance.user).update(is_default=False)
            
        return super().update(instance, validated_data)


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        
    def validate(self, attrs):
        """验证两次密码是否一致"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不一致"})
        
        # 检查用户名或邮箱是否已存在
        if User.objects.filter(Q(username=attrs['username']) | Q(email=attrs['email'])).exists():
            raise serializers.ValidationError({"username": "该用户名或邮箱已被注册"})
            
        return attrs
        
    def create(self, validated_data):
        """创建用户对象，设置密码"""
        # 移除password2字段
        validated_data.pop('password2', None)
        
        # 创建用户对象
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # 设置密码
        user.set_password(validated_data['password'])
        user.save()
        
        return user
