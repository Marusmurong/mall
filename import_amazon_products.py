import os
import json
import django
import decimal
from pathlib import Path

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入模型
from goods.models import Goods, GoodsCategory, GoodsImage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction

def import_amazon_products():
    """
    导入Amazon商品数据到系统中
    """
    # 加载JSON文件
    data_file = Path('/Users/jimmu/mall/scraper/scraped_data/amazon/details/amazon_details_batch_1.json')
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取或创建"Home Life"顶级分类
    home_life_category, created = GoodsCategory.objects.get_or_create(
        name='Home Life',
        defaults={
            'level': 1,
            'description': 'Home lifestyle products and accessories'
        }
    )
    
    # 获取或创建"Mugs & Cups"作为Home Life的子分类
    mugs_category, created = GoodsCategory.objects.get_or_create(
        name='Mugs & Cups',
        defaults={
            'level': 2,
            'parent': home_life_category,
            'description': 'Various mugs and cups for beverages'
        }
    )
    
    # 计数器
    imported_count = 0
    error_count = 0
    
    # 导入每个商品
    for product in data['products']:
        try:
            with transaction.atomic():
                # 提取价格并转换为小数
                price_str = product['price'].replace('$', '')
                
                # 处理空价格或无效价格的情况
                if not price_str or price_str.strip() == '':
                    price = decimal.Decimal('19.99')  # 设置默认价格
                    print(f"Warning: No price found for product '{product['title'][:50]}...', using default price $19.99")
                else:
                    # 确保移除所有非数字字符(除了小数点)
                    price_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
                    price = decimal.Decimal(price_str)
                
                # 截断标题，确保不超过200个字符
                title = product['title']
                if len(title) > 200:
                    title = title[:197] + "..."
                
                # 创建商品记录
                goods = Goods(
                    name=title,
                    category=mugs_category,
                    price=price,
                    original_price=price * decimal.Decimal('1.2'),  # 原价设为当前价格的1.2倍
                    stock=100,  # 默认库存为100
                    description=extract_short_description(product['description']),
                    goods_desc=product['description'],
                    source_url=product['source_url'][:500] if len(product['source_url']) > 500 else product['source_url'],
                    status='published',  # 直接发布
                    is_recommended=True,
                    is_hot=False,
                    is_new=True,
                )
                goods.save()
                
                # 添加商品图片
                if 'images' in product and product['images']:
                    for i, image_name in enumerate(product['images']):
                        # 图片路径
                        image_path = Path('/Users/jimmu/mall/scraper/scraped_data/amazon/images') / image_name
                        
                        # 检查图片是否存在
                        if not image_path.exists():
                            print(f"Image not found: {image_path}")
                            continue
                        
                        # 创建商品图片
                        with open(image_path, 'rb') as img_file:
                            image_content = img_file.read()
                            
                            # 设置是否为主图
                            is_main = (i == 0)
                            
                            # 创建商品图片记录
                            goods_image = GoodsImage(
                                goods=goods,
                                is_main=is_main,
                                sort_order=i
                            )
                            
                            # 保存图片文件
                            image_filename = os.path.basename(image_name)
                            goods_image.image.save(
                                image_filename,
                                ContentFile(image_content),
                                save=True
                            )
                            
                            # 如果是主图，也设置给商品
                            if is_main:
                                goods.image = goods_image.image
                                goods.save(update_fields=['image'])
                
                imported_count += 1
                print(f"Successfully imported: {goods.name} - Price: ${price}")
                
        except Exception as e:
            error_count += 1
            print(f"Error importing product: {product['title'][:100]}...")
            print(f"Error details: {str(e)}")
    
    print(f"\nImport completed: {imported_count} products imported, {error_count} errors.")

def extract_short_description(description):
    """
    从描述中提取简短描述
    """
    # 查找 "About this item" 部分后面的内容
    if "About this item" in description:
        # 找到第一个列表项
        start_idx = description.find("<li class=")
        if start_idx != -1:
            # 查找第一个列表项结束的位置
            end_idx = description.find("</span></li>", start_idx)
            if end_idx != -1:
                # 提取文本内容
                item_html = description[start_idx:end_idx+12]
                # 提取纯文本内容
                import re
                item_text = re.sub('<[^<]+?>', '', item_html).strip()
                # 限制长度
                short_desc = item_text[:200] + "..." if len(item_text) > 200 else item_text
                return short_desc
    
    # 如果找不到，返回一个默认描述
    return "High-quality imported products, please check the detailed description for more information."

if __name__ == '__main__':
    import_amazon_products() 