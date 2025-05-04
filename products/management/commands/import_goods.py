import json
import os
from django.core.management.base import BaseCommand
from products.models import Product, ProductImage, Category
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import products from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file containing product data')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            
            self.stdout.write(self.style.SUCCESS(f'Loaded {len(products_data)} products from file'))
            
            # 计数器
            created_count = 0
            updated_count = 0
            error_count = 0
            
            for product_data in products_data:
                try:
                    # 获取或创建类别
                    category_name = product_data.get('category', 'Uncategorized')
                    category, _ = Category.objects.get_or_create(name=category_name)
                    
                    # 检查产品是否已存在
                    product_id = product_data.get('id')
                    product_sku = product_data.get('sku')
                    
                    product = None
                    if product_id:
                        try:
                            product = Product.objects.get(id=product_id)
                            self.stdout.write(f'Updating existing product ID: {product_id}')
                            updated_count += 1
                        except Product.DoesNotExist:
                            pass
                    
                    if not product and product_sku:
                        try:
                            product = Product.objects.get(sku=product_sku)
                            self.stdout.write(f'Updating existing product SKU: {product_sku}')
                            updated_count += 1
                        except Product.DoesNotExist:
                            pass
                    
                    # 如果产品不存在，创建新产品
                    if not product:
                        product = Product()
                        created_count += 1
                    
                    # 更新产品字段
                    product.name = product_data.get('name', '')
                    product.description = product_data.get('description', '')
                    product.price = float(product_data.get('price', 0))
                    product.sale_price = float(product_data.get('sale_price', 0)) if product_data.get('sale_price') else None
                    product.sku = product_data.get('sku', '')
                    product.stock = int(product_data.get('stock', 0))
                    product.category = category
                    
                    # 设置为发布状态
                    product.is_active = True
                    product.published_at = timezone.now()
                    
                    # 保存产品
                    product.save()
                    
                    # 处理图片
                    images = product_data.get('images', [])
                    if images:
                        # 清除现有图片
                        ProductImage.objects.filter(product=product).delete()
                        
                        # 添加新图片
                        for i, image_url in enumerate(images):
                            ProductImage.objects.create(
                                product=product,
                                image=image_url,
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
            self.stdout.write(self.style.ERROR(f'Failed to import products: {str(e)}'))
