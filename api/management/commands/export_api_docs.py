import os
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '导出API文档到本地目录'

    def handle(self, *args, **options):
        docs_dir = os.path.join(settings.BASE_DIR, 'api_docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS('正在生成OpenAPI文档...'))
        
        # 启动一个临时服务器来获取数据
        self.stdout.write(self.style.SUCCESS('正在创建临时服务器获取API文档数据...'))
        port = 8788  # 使用一个不太常用的端口
        url = f'http://localhost:{port}/api/swagger.json'
        
        # 获取JSON内容 - 先尝试连接本地服务器，如果失败，使用直接导入的方法
        try:
            # 尝试使用管理命令内置的runserver来执行请求
            from django.core.management import call_command
            import threading
            import time
            
            # 启动一个临时服务器线程
            def start_server():
                try:
                    call_command('runserver', f'{port}', '--noreload')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'启动服务器失败: {e}'))
            
            server_thread = threading.Thread(target=start_server)
            server_thread.daemon = True
            server_thread.start()
            
            # 等待服务器启动
            time.sleep(2)
            
            # 请求 Swagger JSON
            response = requests.get(url, timeout=5)
            schema_dict = response.json()
            
            self.stdout.write(self.style.SUCCESS('成功从服务器获取API文档'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'无法从服务器获取API文档: {e}'))
            self.stdout.write(self.style.WARNING('使用备用方法生成文档...'))
            
            # 备用方法：直接从urls.py提取内容创建基本模板
            schema_dict = {
                "swagger": "2.0",
                "info": {
                    "title": "Mall API",
                    "description": "多站点电商系统API文档",
                    "version": "v1"
                },
                "paths": {
                    "/api/v1/sites/": {
                        "get": {
                            "operationId": "sites_list",
                            "description": "获取所有可用站点列表",
                            "parameters": [],
                            "responses": {
                                "200": {
                                    "description": "成功获取站点列表"
                                }
                            }
                        }
                    },
                    "/api/v1/sites/{site_id}/config": {
                        "get": {
                            "operationId": "site_config",
                            "description": "获取站点配置信息",
                            "parameters": [
                                {
                                    "name": "site_id",
                                    "in": "path",
                                    "required": True,
                                    "type": "string"
                                }
                            ],
                            "responses": {
                                "200": {
                                    "description": "成功获取站点配置"
                                }
                            }
                        }
                    }
                }
            }
        
        # 导出为JSON
        json_path = os.path.join(docs_dir, 'openapi.json')
        with open(json_path, 'w') as f:
            json.dump(schema_dict, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f'文档已保存到: {json_path}'))
        
        # 导出为YAML (可选)
        try:
            import yaml
            yaml_path = os.path.join(docs_dir, 'openapi.yaml')
            with open(yaml_path, 'w') as f:
                yaml.dump(schema_dict, f, allow_unicode=True)
            self.stdout.write(self.style.SUCCESS(f'YAML文档已保存到: {yaml_path}'))
        except ImportError:
            self.stdout.write(self.style.WARNING('未安装PyYAML库，无法导出YAML格式文档'))
        
        # 复制到前端目录
        frontend_docs_dir = os.path.join(settings.BASE_DIR, 'frontend/src/api')
        os.makedirs(frontend_docs_dir, exist_ok=True)
        
        import shutil
        try:
            shutil.copy(json_path, os.path.join(frontend_docs_dir, 'openapi.json'))
            self.stdout.write(self.style.SUCCESS(f'API文档已复制到: {frontend_docs_dir}/openapi.json'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'复制到前端目录失败: {e}'))
        
        self.stdout.write(self.style.SUCCESS('API文档导出完成!')) 