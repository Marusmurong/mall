from rest_framework.renderers import JSONRenderer
from django.conf import settings

class APIJSONRenderer(JSONRenderer):
    """
    自定义JSON渲染器，确保所有响应都具有统一的格式
    {
      "code": 0,
      "message": "success",
      "data": {...}
    }
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        重写render方法，包装响应数据为统一格式
        """
        response_format = getattr(settings, 'API_RESPONSE_FORMAT', {
            'CODE_FIELD': 'code',
            'MESSAGE_FIELD': 'message',
            'DATA_FIELD': 'data',
            'SUCCESS_CODE': 0,
            'ERROR_CODE': 1,
            'SUCCESS_MESSAGE': 'success',
        })
        
        # 获取状态码
        status_code = renderer_context['response'].status_code
        
        # 获取字段名
        code_field = response_format.get('CODE_FIELD', 'code')
        message_field = response_format.get('MESSAGE_FIELD', 'message')
        data_field = response_format.get('DATA_FIELD', 'data')
        success_code = response_format.get('SUCCESS_CODE', 0)
        error_code = response_format.get('ERROR_CODE', 1)
        success_message = response_format.get('SUCCESS_MESSAGE', 'success')
        
        # 检查是否已经是标准格式
        if isinstance(data, dict) and code_field in data and message_field in data and data_field in data:
            response = data
        else:
            # 成功响应
            if 200 <= status_code < 300:
                response = {
                    code_field: success_code,
                    message_field: success_message,
                    data_field: data or {}
                }
            # 失败响应
            else:
                # 处理DRF错误响应格式
                if isinstance(data, dict) and 'detail' in data:
                    message = data['detail']
                elif isinstance(data, dict) and any(isinstance(data.get(k), list) for k in data):
                    # 字段错误格式化
                    message = {}
                    for field, errors in data.items():
                        if isinstance(errors, list):
                            message[field] = errors[0] if errors else ''
                else:
                    message = data if isinstance(data, str) else 'Error'
                
                response = {
                    code_field: error_code,
                    message_field: message,
                    data_field: {}
                }
                
        # 使用父类的render方法来序列化为JSON
        return super().render(response, accepted_media_type, renderer_context)
