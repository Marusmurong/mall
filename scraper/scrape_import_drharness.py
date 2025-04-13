#!/usr/bin/env python
"""
DrHarness数据导入脚本: 将采集的数据导入到数据库
"""
import os
import sys
import json
import logging
import django
from pathlib import Path
from datetime import datetime

# 确保可以导入Django项目
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入Django模型
from goods.models import GoodsCategory, Goods, GoodsImage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("drharness_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
IMAGES_DIR = "scraped_images/drharness"
DATA_FILE = "drharness_all_products.json"
CATEGORIES_FILE = "drharness_categories.json"
DEFAULT_PARENT_CATEGORY_NAME = "Leather Lingerie & Accessories"  # 默认顶级分类名称


def import_categories(categories_data=None):
    """导入分类数据到数据库"""
    if categories_data is None:
        # 如果没有提供分类数据，尝试从文件加载
        try:
            with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                categories_data = json.load(f)
            logger.info(f"从文件加载了 {len(categories_data)} 个分类数据")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"无法加载分类数据: {e}")
            return []

    # 创建或获取顶级父分类
    parent_category, created = GoodsCategory.objects.get_or_create(
        name=DEFAULT_PARENT_CATEGORY_NAME,
        defaults={
            'code': 'drharness',
            'desc': 'Leather lingerie and accessories from DrHarness',
            'category_type': 1,  # 一级分类
            'is_tab': True
        }
    )
    if created:
        logger.info(f"创建了顶级分类: {DEFAULT_PARENT_CATEGORY_NAME}")
    else:
        logger.info(f"使用已存在的顶级分类: {DEFAULT_PARENT_CATEGORY_NAME}")

    # 导入所有子分类
    imported_categories = []
    for category_data in categories_data:
        category_name = category_data['name']
        
        # 跳过名称中包含"New"的分类
        if "new" in category_name.lower():
            logger.info(f"跳过'New'分类: {category_name}")
            continue
        
        try:
            # 创建或获取分类
            category, created = GoodsCategory.objects.get_or_create(
                name=category_name,
                defaults={
                    'code': category_name.lower().replace(' ', '_'),
                    'desc': f"DrHarness {category_name}",
                    'category_type': 2,  # 二级分类
                    'parent_category': parent_category,
                    'is_tab': False
                }
            )
            
            if created:
                logger.info(f"创建了新分类: {category_name}")
            else:
                logger.info(f"使用已存在的分类: {category_name}")
                
            # 更新分类URL
            if 'url' in category_data and category_data['url']:
                category.source_url = category_data['url']
                category.save(update_fields=['source_url'])
                
            imported_categories.append(category)
        except Exception as e:
            logger.error(f"导入分类 '{category_name}' 时出错: {e}")
    
    return imported_categories


def import_products(products_data=None):
    """导入商品数据到数据库"""
    if products_data is None:
        # 如果没有提供商品数据，尝试从文件加载
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            logger.info(f"从文件加载了 {len(products_data)} 个商品数据")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"无法加载商品数据: {e}")
            return

    # 统计信息
    products_imported = 0
    products_updated = 0
    products_skipped = 0
    images_imported = 0
    
    for product_data in products_data:
        try:
            # 获取必要字段
            title = product_data.get('title', '')
            if not title:
                logger.warning(f"跳过没有标题的商品")
                products_skipped += 1
                continue
                
            # 获取分类
            category_name = product_data.get('category', '')
            if not category_name:
                logger.warning(f"商品 '{title}' 没有指定分类，使用默认分类")
                category_name = DEFAULT_PARENT_CATEGORY_NAME
            
            # 尝试查找匹配的分类，首先查找二级分类
            try:
                category = GoodsCategory.objects.get(name=category_name)
            except GoodsCategory.DoesNotExist:
                # 如果找不到，使用顶级分类
                logger.warning(f"找不到分类 '{category_name}'，使用顶级分类")
                category, _ = GoodsCategory.objects.get_or_create(
                    name=DEFAULT_PARENT_CATEGORY_NAME
                )
            
            # 准备商品数据
            source_url = product_data.get('url', '')
            description = product_data.get('description', '')
            price = product_data.get('price_usd', 0)
            if not price and 'price_original' in product_data:
                price = float(product_data['price_original'])
            
            in_stock = product_data.get('in_stock', True)
            status = 'published' if in_stock else 'off_shelf'
            
            # 处理图片
            local_images = product_data.get('local_images', [])
            
            # 创建或更新商品
            defaults = {
                'category': category,
                'goods_desc': description,
                'description': description,
                'price': price,
                'original_price': price,
                'source_url': source_url,
                'status': status,
                'is_recommended': True,
                'is_hot': in_stock,
                'is_new': True,
                'stock': 100  # 设置默认库存
            }
            
            goods, created = Goods.objects.get_or_create(
                name=title,
                defaults=defaults
            )
            
            if created:
                logger.info(f"创建了新商品: {title}")
                products_imported += 1
            else:
                # 更新现有商品
                for key, value in defaults.items():
                    setattr(goods, key, value)
                goods.save()
                logger.info(f"更新了现有商品: {title}")
                products_updated += 1
            
            # 处理商品图片
            for i, img_path in enumerate(local_images):
                try:
                    if not img_path:
                        continue
                        
                    # 设置全路径（不含scraped_images/前缀）
                    img_path = os.path.join('drharness', img_path)
                    
                    # 创建或更新图片
                    image, img_created = GoodsImage.objects.get_or_create(
                        goods=goods,
                        image=img_path,
                        defaults={
                            'is_main': i == 0,  # 第一张图设为主图
                            'sort_order': i
                        }
                    )
                    
                    if img_created:
                        images_imported += 1
                    
                    # 如果商品还没有主图，设置第一张图为主图
                    if i == 0 and not goods.image:
                        goods.image = img_path
                        goods.save(update_fields=['image'])
                        
                except Exception as e:
                    logger.error(f"处理商品 '{title}' 的图片 '{img_path}' 时出错: {e}")
            
        except Exception as e:
            logger.error(f"导入商品时出错: {e}")
            products_skipped += 1
    
    # 打印统计信息
    logger.info(f"==== 商品导入完成 ====")
    logger.info(f"- 新增商品: {products_imported}")
    logger.info(f"- 更新商品: {products_updated}")
    logger.info(f"- 跳过商品: {products_skipped}")
    logger.info(f"- 导入图片: {images_imported}")
    
    return {
        'imported': products_imported,
        'updated': products_updated,
        'skipped': products_skipped,
        'images': images_imported
    }


def main():
    """主函数"""
    start_time = datetime.now()
    
    logger.info("=== 开始导入DrHarness数据到数据库 ===")
    
    # 1. 导入分类
    logger.info("正在导入分类...")
    imported_categories = import_categories()
    logger.info(f"成功导入 {len(imported_categories)} 个分类")
    
    # 2. 导入商品
    logger.info("正在导入商品...")
    import_stats = import_products()
    
    # 计算耗时
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=== DrHarness数据导入完成! ===")
    logger.info(f"总耗时: {duration:.2f} 秒")
    
    return import_stats


if __name__ == "__main__":
    main() 