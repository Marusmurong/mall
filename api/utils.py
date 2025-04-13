from django.conf import settings

def get_current_site():
    """获取当前站点ID"""
    # 在实际应用中，这个函数应该从请求对象中获取站点信息
    # 这里简化处理，返回默认站点
    return 'alokai'  # Alokai站点ID
