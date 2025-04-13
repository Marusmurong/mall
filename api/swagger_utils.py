"""
Swagger文档生成工具

提供适配Swagger文档生成的工具函数和mixins
"""
from functools import wraps

def swagger_safe_queryset(get_queryset_func):
    """
    装饰器，使get_queryset方法在Swagger文档生成时返回简化的查询集
    避免执行复杂的数据库操作，特别是不同数据库后端可能不支持的JSON操作
    """
    @wraps(get_queryset_func)
    def wrapper(self, *args, **kwargs):
        # 检测是否在Swagger文档生成过程中
        if getattr(self, 'swagger_fake_view', False):
            # 在Swagger文档生成时返回基本的查询集
            # 对于ModelViewSet，直接返回模型的基本查询集
            if hasattr(self, 'queryset') and self.queryset is not None:
                return self.queryset.model.objects.none()
                
            # 如果没有预定义的queryset，返回空查询集
            return None
            
        # 正常环境下执行原始方法
        return get_queryset_func(self, *args, **kwargs)
        
    return wrapper

class SwaggerSafeViewSetMixin:
    """
    混入类，使视图集在Swagger文档生成时安全处理查询集
    """
    def get_queryset(self):
        """获取查询集，对Swagger文档生成进行特殊处理"""
        # 检测是否在Swagger文档生成过程中
        if getattr(self, 'swagger_fake_view', False):
            # 在Swagger文档生成时返回基本的查询集
            if hasattr(self, 'queryset') and self.queryset is not None:
                return self.queryset.model.objects.none()
            return None
            
        # 正常情况下调用父类方法
        return super().get_queryset()
        
def apply_swagger_fixes():
    """
    全局应用Swagger修复
    修改所有视图集的get_queryset方法，使其在Swagger文档生成时返回简化的查询集
    """
    from rest_framework import viewsets
    from rest_framework.views import APIView
    
    # 保存原始的get_queryset方法
    original_get_queryset = viewsets.GenericViewSet.get_queryset
    
    # 定义新的get_queryset方法
    @wraps(original_get_queryset)
    def safe_get_queryset(self):
        # 检测是否在Swagger文档生成过程中
        if getattr(self, 'swagger_fake_view', False):
            # 在Swagger文档生成时返回基本的查询集
            if hasattr(self, 'queryset') and self.queryset is not None:
                return self.queryset.model.objects.none()
            return None
            
        # 正常情况下调用原始方法
        return original_get_queryset(self)
    
    # 应用修复
    viewsets.GenericViewSet.get_queryset = safe_get_queryset
    
    print("Applied Swagger fixes to all viewsets.")
