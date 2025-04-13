from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """在应用准备就绪时执行初始化操作"""
        # 应用Swagger文档生成修复
        try:
            from .swagger_utils import apply_swagger_fixes
            apply_swagger_fixes()
            print("Swagger文档生成修复已应用")
        except Exception as e:
            print(f"Swagger文档生成修复应用失败: {e}")
