from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.conf import settings

def custom_exception_handler(exc, context):
    """
    自定义异常处理函数
    处理所有API异常，将它们转换为统一的响应格式
    """
    # 调用DRF默认的异常处理方法获取标准响应
    response = exception_handler(exc, context)
    
    # 如果默认处理方法无法处理，则使用我们自己的通用处理逻辑
    if response is None:
        # 获取异常数据
        if isinstance(exc, APIException):
            data = {'detail': exc.detail}
            status_code = exc.status_code
        else:
            # 其他未处理的异常
            data = {'detail': str(exc)}
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # 获取响应格式设置
        response_format = getattr(settings, 'API_RESPONSE_FORMAT', {
            'CODE_FIELD': 'code',
            'MESSAGE_FIELD': 'message',
            'DATA_FIELD': 'data',
            'ERROR_CODE': 1,
        })
        
        code_field = response_format.get('CODE_FIELD', 'code')
        message_field = response_format.get('MESSAGE_FIELD', 'message')
        data_field = response_format.get('DATA_FIELD', 'data')
        error_code = response_format.get('ERROR_CODE', 1)
        
        # 构建新的统一错误响应
        error_response = {
            code_field: error_code,
            message_field: data['detail'],
            data_field: {}
        }
        
        from rest_framework.response import Response
        response = Response(error_response, status=status_code)
    
    return response

class BusinessException(APIException):
    """
    业务逻辑异常类
    用于封装所有业务层面的错误，转换为API错误响应
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '业务处理失败'
    default_code = 'business_error'
    
    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail, code)
