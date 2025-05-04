"""
Swagger文档生成修复工具

用于解决Swagger文档生成时遇到的未认证用户处理问题
"""
"""Swagger文档生成修复工具

用于解决Swagger文档生成时遇到的未认证用户处理问题，使用认证类和中间件拦截器
"""
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import json
import logging

logger = logging.getLogger(__name__)
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
        
        # 如果请求的是Swagger格式化文档，并且请求可能导致外部连接问题
        if 'swagger' in request.path and 'format=openapi' in request.path:
            try:
                response = self.get_response(request)
                return response
            except Exception as e:
                logger.error(f"Swagger文档生成错误: {str(e)}")
                # 返回一个简化的API文档JSON
                return JsonResponse({
                    "openapi": "3.0.0",
                    "info": {
                        "title": "API文档 (本地版本)",
                        "description": "由于网络原因无法加载完整API文档，这是简化版本",
                        "version": "v1"
                    },
                    "paths": {
                        "/api/v1/auth/token/": {
                            "post": {
                                "summary": "用户登录接口",
                                "description": "通过用户名和密码获取JWT令牌"
                            }
                        },
                        "/api/v1/user/register/": {
                            "post": {
                                "summary": "用户注册接口",
                                "description": "创建新用户，需要邀请码"
                            }
                        }
                    }
                })
        
        return self.get_response(request)
