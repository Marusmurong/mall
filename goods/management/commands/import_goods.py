import json
import os
from django.core.management.base import BaseCommand
from goods.models import Goods, GoodsImage, GoodsCategory
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import goods from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file containing goods data')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
        
        try:
            # 读取文件内容
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找 JSON 数组的开始位置 (第一个 '[')
            start_pos = content.find('[')
            if start_pos == -1:
                self.stdout.write(self.style.ERROR(f'Invalid JSON format: no array found'))
                return
            
            # 提取 JSON 部分
            json_content = content[start_pos:]
            
            # 解析 JSON
            goods_data = json.loads(json_content)
            
            self.stdout.write(self.style.SUCCESS(f'Loaded {len(goods_data)} goods from file'))
            
            # 计数器
            created_count = 0
            updated_count = 0
            error_count = 0
            
            for item_data in goods_data:
                try:
                    # 获取或创建类别
                    category_name = item_data.get('category', 'Uncategorized')
                    category, _ = GoodsCategory.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'level': 1,
                            'is_active': True,
                            'sort_order': 0
                        }
                    )
                    
                    # 检查商品是否已存在
                    product_id = item_data.get('id')
                    
                    product = None
                    if product_id:
                        try:
                            product = Goods.objects.get(id=product_id)
                            self.stdout.write(f'Updating existing product ID: {product_id}')
                            updated_count += 1
                        except Goods.DoesNotExist:
                            pass
                    
                    # 如果产品不存在，创建新产品
                    if not product:
                        product = Goods()
                        created_count += 1
                    
                    # 更新产品字段
                    product.name = item_data.get('name', '')
                    product.description = item_data.get('description', '')
                    product.goods_desc = item_data.get('goods_desc', item_data.get('description', ''))
                    product.price = float(item_data.get('price', 0))
                    product.original_price = float(item_data.get('original_price', item_data.get('price', 0)))
                    product.stock = int(item_data.get('stock', 0))
                    product.category = category
                    product.source_url = item_data.get('source_url', '')
                    
                    # 设置为发布状态
                    product.status = 'published'
                    
                    # 保存产品
                    product.save()
                    
                    # 处理图片
                    images = item_data.get('images', [])
                    if images:
                        # 清除现有图片
                        GoodsImage.objects.filter(goods=product).delete()
                        
                        # 添加新图片
                        for i, image_url in enumerate(images):
                            GoodsImage.objects.create(
                                goods=product,
                                image=image_url,
                                is_main=(i == 0),  # 第一张图片设为主图
                                sort_order=i
                            )
                    
                    self.stdout.write(f'Successfully processed product: {product.name}')
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing product: {str(e)}'))
                    error_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'Import completed: {created_count} created, {updated_count} updated, {error_count} errors'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import goods: {str(e)}'))
