import json
import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction

class Command(BaseCommand):
    help = '从Django dumpdata格式的JSON文件导入数据'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Django dumpdata格式的JSON文件路径')
        parser.add_argument('--limit', type=int, default=None, help='限制导入的记录数量')
        parser.add_argument('--dry-run', action='store_true', help='只显示将导入的数据，不实际导入')
        parser.add_argument('--model-filter', type=str, default=None, help='只导入指定模型的数据，例如 goods.goods')

    def handle(self, *args, **options):
        json_file = options['json_file']
        limit = options['limit']
        dry_run = options['dry_run']
        model_filter = options['model_filter']
        
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'文件不存在: {json_file}'))
            return
        
        try:
            # 读取文件内容
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找JSON数组的开始位置
            start_pos = content.find('[')
            if start_pos == -1:
                self.stdout.write(self.style.ERROR(f'无效的JSON格式: 未找到数组'))
                return
            
            # 提取JSON部分
            json_content = content[start_pos:]
            
            # 解析JSON
            data = json.loads(json_content)
            
            # 按模型分组
            models = {}
            for item in data:
                model_name = item.get('model')
                if not model_name:
                    continue
                
                if model_filter and model_name != model_filter:
                    continue
                
                if model_name not in models:
                    models[model_name] = []
                
                models[model_name].append(item)
            
            total_count = sum(len(items) for items in models.values())
            self.stdout.write(self.style.SUCCESS(f'从文件中加载了 {total_count} 条记录，涉及 {len(models)} 个模型'))
            
            # 显示每个模型的记录数
            for model_name, items in models.items():
                self.stdout.write(f'模型 {model_name}: {len(items)} 条记录')
            
            if dry_run:
                self.stdout.write(self.style.WARNING('这是一个预演，没有导入任何数据'))
                self.stdout.write(self.style.WARNING('使用 python manage.py import_django_data 文件路径 命令来实际导入数据'))
                return
            
            # 开始导入数据
            with transaction.atomic():
                for model_name, items in models.items():
                    try:
                        app_label, model_name_short = model_name.split('.')
                        model_class = apps.get_model(app_label, model_name_short)
                        
                        self.stdout.write(f'正在导入 {model_name_short} 数据...')
                        
                        # 限制记录数量
                        if limit:
                            items = items[:limit]
                        
                        # 导入数据
                        imported_count = 0
                        for item in items:
                            pk = item.get('pk')
                            fields = item.get('fields', {})
                            
                            # 处理外键关系
                            for field_name, field_value in list(fields.items()):
                                try:
                                    field = model_class._meta.get_field(field_name)
                                    
                                    # 如果是外键字段且值不为None
                                    if field.is_relation and field.many_to_one and field_value is not None:
                                        try:
                                            # 获取关联模型
                                            related_model = field.related_model
                                            # 查找关联对象
                                            related_obj = related_model.objects.get(pk=field_value)
                                            # 替换为实际对象
                                            fields[field_name] = related_obj
                                        except related_model.DoesNotExist:
                                            self.stdout.write(self.style.WARNING(f'  关联对象不存在: {field_name}={field_value}'))
                                            # 如果关联对象不存在，设为None
                                            fields[field_name] = None
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'  处理字段 {field_name} 时出错: {str(e)}'))
                                    # 如果处理出错，移除该字段
                                    fields.pop(field_name, None)
                            
                            # 检查记录是否已存在
                            try:
                                obj = model_class.objects.get(pk=pk)
                                # 更新现有记录
                                for field, value in fields.items():
                                    setattr(obj, field, value)
                                obj.save()
                                self.stdout.write(f'  更新记录: {model_name_short} #{pk}')
                            except model_class.DoesNotExist:
                                # 创建新记录
                                new_obj = model_class(pk=pk, **fields)
                                new_obj.save()
                                self.stdout.write(f'  创建记录: {model_name_short} #{pk}')
                            
                            imported_count += 1
                            
                            # 每100条记录显示一次进度
                            if imported_count % 100 == 0:
                                self.stdout.write(f'  已导入 {imported_count}/{len(items)} 条记录...')
                        
                        self.stdout.write(self.style.SUCCESS(f'成功导入 {imported_count} 条 {model_name_short} 记录'))
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'导入 {model_name} 数据时出错: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS('导入完成'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导入数据失败: {str(e)}'))
