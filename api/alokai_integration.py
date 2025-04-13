"""
Alokai API管理平台集成配置

这个模块提供与Alokai API管理平台集成所需的配置和工具函数。
根据Alokai的具体集成方式，可能需要调整此配置。
"""

import json
import logging
import requests
from django.conf import settings
from rest_framework.response import Response
from functools import wraps

logger = logging.getLogger(__name__)

# Alokai API网关配置
ALOKAI_CONFIG = {
    'api_key': getattr(settings, 'ALOKAI_API_KEY', ''),
    'secret': getattr(settings, 'ALOKAI_SECRET', ''),
    'gateway_url': getattr(settings, 'ALOKAI_GATEWAY_URL', 'https://api.alokai.example.com'),
    'service_name': getattr(settings, 'ALOKAI_SERVICE_NAME', 'mall-multi-site-api'),
}

def register_api_with_alokai(api_name, api_path, methods, description=''):
    """
    向Alokai注册一个API端点
    
    Args:
        api_name: API名称
        api_path: API路径
        methods: 支持的HTTP方法列表
        description: API描述
    
    Returns:
        bool: 是否注册成功
    """
    if not ALOKAI_CONFIG['api_key']:
        logger.warning("Alokai API Key未配置，无法注册API")
        return False
    
    try:
        payload = {
            'name': api_name,
            'path': api_path,
            'methods': methods,
            'description': description,
            'service': ALOKAI_CONFIG['service_name']
        }
        
        # 这里应该根据Alokai的实际API调整请求
        response = requests.post(
            f"{ALOKAI_CONFIG['gateway_url']}/register", 
            headers={
                'X-API-Key': ALOKAI_CONFIG['api_key'],
                'Content-Type': 'application/json'
            },
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            logger.info(f"API {api_name} 注册到Alokai成功")
            return True
        else:
            logger.error(f"API {api_name} 注册到Alokai失败: {response.text}")
            return False
            
    except Exception as e:
        logger.exception(f"注册API到Alokai时发生错误: {str(e)}")
        return False

def alokai_api_monitoring(view_func):
    """
    装饰器，用于API调用监控和分析
    将API调用数据发送到Alokai
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        import time
        start_time = time.time()
        
        # 调用原始视图函数
        response = view_func(request, *args, **kwargs)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 如果配置了Alokai，发送监控数据
        if ALOKAI_CONFIG['api_key']:
            try:
                # 提取请求信息
                endpoint = request.path
                method = request.method
                status_code = response.status_code if hasattr(response, 'status_code') else 200
                
                # 准备监控数据
                monitoring_data = {
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': status_code,
                    'execution_time': execution_time,
                    'timestamp': time.time(),
                    'service': ALOKAI_CONFIG['service_name']
                }
                
                # 异步发送监控数据（在实际应用中应该使用异步任务）
                # 这里使用一个简单的线程来模拟异步
                import threading
                def send_monitoring_data():
                    try:
                        requests.post(
                            f"{ALOKAI_CONFIG['gateway_url']}/metrics", 
                            headers={
                                'X-API-Key': ALOKAI_CONFIG['api_key'],
                                'Content-Type': 'application/json'
                            },
                            data=json.dumps(monitoring_data),
                            timeout=2  # 设置短超时，避免影响主请求
                        )
                    except Exception as e:
                        logger.error(f"发送监控数据到Alokai失败: {str(e)}")
                
                # 启动线程发送数据
                threading.Thread(target=send_monitoring_data).start()
                
            except Exception as e:
                logger.exception(f"处理Alokai监控数据时发生错误: {str(e)}")
        
        return response
    
    return wrapper

def export_openapi_to_alokai():
    """
    将OpenAPI/Swagger文档导出到Alokai
    """
    from drf_yasg.generators import OpenAPISchemaGenerator
    from django.urls import get_resolver
    
    if not ALOKAI_CONFIG['api_key']:
        logger.warning("Alokai API Key未配置，无法导出API文档")
        return False
    
    try:
        # 生成OpenAPI文档
        generator = OpenAPISchemaGenerator()
        schema = generator.get_schema()
        schema_json = json.dumps(schema)
        
        # 发送到Alokai
        response = requests.post(
            f"{ALOKAI_CONFIG['gateway_url']}/import-openapi", 
            headers={
                'X-API-Key': ALOKAI_CONFIG['api_key'],
                'Content-Type': 'application/json'
            },
            data=schema_json
        )
        
        if response.status_code == 200:
            logger.info("OpenAPI文档成功导出到Alokai")
            return True
        else:
            logger.error(f"导出OpenAPI文档到Alokai失败: {response.text}")
            return False
            
    except Exception as e:
        logger.exception(f"导出OpenAPI文档到Alokai时发生错误: {str(e)}")
        return False
