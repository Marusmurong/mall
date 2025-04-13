"""
Swagger文档生成修复工具

用于解决Swagger文档生成时遇到的未认证用户处理问题
"""
"""Swagger文档生成修复工具

用于解决Swagger文档生成时遇到的未认证用户处理问题，使用认证类和中间件拦截器
"""
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

User = get_user_model()

class SwaggerFixAuthentication(BaseAuthentication):
    """为Swagger文档请求提供测试用户认证"""
    
    def authenticate(self, request):
        # 如果是swagger文档请求，返回一个测试用户
        if 'swagger' in request.path or 'openapi' in request.path:
            # 创建一个测试用户
            test_user = User(id=1, username='swagger_test_user')
            return (test_user, None)
        
        # 这里返回None表示此认证类不处理其他请求
        # 会让请求继续到下一个认证类
        return None
        
class SwaggerFixMiddleware:
    """中间件，为Swagger文档请求提供测试用户"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 如果是swagger文档请求且用户未认证
        if ('swagger' in request.path or 'openapi' in request.path) and isinstance(request.user, AnonymousUser):
            # 创建一个测试用户
            request.user = User(id=1, username='swagger_test_user')
            
        return self.get_response(request)
