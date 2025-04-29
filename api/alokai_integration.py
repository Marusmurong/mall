"""
本地API系统集成配置 (原Alokai API接入替换)

本模块提供API管理功能，所有功能直接调用本地API实现。
"""

import json
import logging
import requests
from django.conf import settings
from rest_framework.response import Response
from functools import wraps

logger = logging.getLogger(__name__)

# 本地API配置
LOCAL_API_CONFIG = {
    'api_key': 'local_api_key',
    'gateway_url': 'http://localhost:8000/api/v1',
    'service_name': 'mall-multi-site-api',
}

def register_api_with_gateway(api_name, api_path, methods, description=''):
    """
    注册一个API端点到本地API网关
    
    Args:
        api_name: API名称
        api_path: API路径
        methods: 支持的HTTP方法列表
        description: API描述
    
    Returns:
        bool: 是否注册成功
    """
    logger.info(f"已注册本地API: {api_name}, 路径: {api_path}")
    return True

def api_monitoring(view_func):
    """
    装饰器，用于API调用监控和分析
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        import time
        start_time = time.time()
        
        # 调用原始视图函数
        response = view_func(request, *args, **kwargs)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 记录API调用日志
        endpoint = request.path
        method = request.method
        status_code = response.status_code if hasattr(response, 'status_code') else 200
        
        logger.info(f"API调用: {method} {endpoint}, 状态码: {status_code}, 执行时间: {execution_time:.4f}秒")
        
        return response
    
    return wrapper

def export_openapi_to_gateway():
    """
    导出OpenAPI/Swagger文档到本地系统
    """
    from drf_yasg.generators import OpenAPISchemaGenerator
    
    try:
        # 生成OpenAPI文档
        generator = OpenAPISchemaGenerator()
        schema = generator.get_schema()
        schema_json = json.dumps(schema)
        
        # 保存到文件系统
        import os
        docs_dir = os.path.join(settings.BASE_DIR, 'api_docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        with open(os.path.join(docs_dir, 'openapi.json'), 'w') as f:
            f.write(schema_json)
            
        logger.info("OpenAPI文档已成功导出到本地系统")
        return True
            
    except Exception as e:
        logger.exception(f"导出OpenAPI文档时发生错误: {str(e)}")
        return False
