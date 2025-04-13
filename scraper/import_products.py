#!/usr/bin/env python
"""
导入脚本：将采集的商品数据导入到Django数据库
"""
import os
import sys
import json
import logging
import django
from datetime import datetime
from decimal import Decimal
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入Django模型
from goods.models import Goods, GoodsCategory, GoodsImage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
DATA_FILE = "scraped_products.json"  # JSON数据文件
IMAGE_DIR = "scraped_images"  # 图片目录

# 创建或获取商品分类
def get_or_create_category(category_name):
    """创建或获取商品分类"""
    try:
        category, created = GoodsCategory.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'商品分类：{category_name}'
            }
        )
        if created:
            logger.info(f"创建了新分类: {category_name}")
        return category
    except Exception as e:
        logger.error(f"创建分类失败: {category_name}, 错误: {e}")
        return None

# 将URL路径映射到分类名称
def map_url_to_category(url):
    """根据URL路径映射到分类名称"""
    mapping = {
        'fetish-wear': '皮革服装',
        'floggers-whips': '鞭子',
        'impact': '冲击器',
        'collars-gags': '项圈与口塞',
        'restraint-cuff-sets': '束缚手铐套装',
        'hoods-masks-and-blindfolds': '头套面具与眼罩',
        'gloves': '手套',
        'leashes-locks-and-accessories': '牵引绳锁和配件',
    }
    
    for key, value in mapping.items():
        if key in url:
            return value
    
    return '其他商品'  # 默认分类

# 从JSON文件导入商品数据
def import_products():
    """从JSON文件导入商品数据"""
    # 检查数据文件是否存在
    if not os.path.exists(DATA_FILE):
        logger.error(f"数据文件不存在: {DATA_FILE}")
        return False
    
    # 读取JSON数据
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        logger.info(f"从 {DATA_FILE} 读取到 {len(products_data)} 个商品")
    except Exception as e:
        logger.error(f"读取数据文件失败: {e}")
        return False
    
    # 统计导入数量
    imported_count = 0
    updated_count = 0
    error_count = 0
    
    # 导入每个商品
    for product in products_data:
        try:
            # 提取商品数据
            product_id = product.get('id')
            title = product.get('title', '未知商品')
            description = product.get('description', '')
            price_str = product.get('price', '0')
            source_url = product.get('source_url', '')
            images = product.get('images', [])
            
            # 处理价格
            try:
                # 移除非数字字符
                price_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
                price = Decimal(price_str)
            except:
                price = Decimal('0.00')
                logger.warning(f"无法解析价格 '{product.get('price')}', 使用默认值 0.00")
            
            # 确定商品分类
            category_name = map_url_to_category(source_url)
            category = get_or_create_category(category_name)
            
            # 检查商品是否已存在（使用标题匹配）
            existing_goods = Goods.objects.filter(name=title).first()
            
            if existing_goods:
                # 更新现有商品
                existing_goods.category = category
                existing_goods.price = price
                existing_goods.goods_desc = description
                existing_goods.source_url = source_url
                existing_goods.updated_at = datetime.now()
                existing_goods.save()
                
                logger.info(f"更新商品: {title}")
                updated_count += 1
                
                # 删除现有图片
                existing_goods.images.all().delete()
            else:
                # 创建新商品
                new_goods = Goods(
                    name=title,
                    category=category,
                    price=price,
                    goods_desc=description,
                    source_url=source_url
                )
                new_goods.save()
                
                logger.info(f"导入商品: {title}")
                imported_count += 1
                existing_goods = new_goods
            
            # 添加商品图片
            for i, image_filename in enumerate(images):
                image_path = os.path.join(IMAGE_DIR, image_filename)
                
                if os.path.exists(image_path):
                    # 创建商品图片记录
                    with open(image_path, 'rb') as img_file:
                        goods_image = GoodsImage(
                            goods=existing_goods,
                            is_main=(i == 0)  # 第一张图片为主图
                        )
                        goods_image.image.save(
                            image_filename,
                            ImageFile(img_file),
                            save=True
                        )
                    
                    logger.info(f"添加图片: {image_filename} 到商品 {title}")
                else:
                    logger.warning(f"图片文件不存在: {image_path}")
            
        except Exception as e:
            logger.error(f"导入商品失败: {product.get('title', 'Unknown')}, 错误: {e}")
            error_count += 1
    
    # 输出统计信息
    logger.info(f"导入完成: 成功导入 {imported_count} 个新商品, 更新 {updated_count} 个现有商品, {error_count} 个错误")
    return True

if __name__ == "__main__":
    logger.info("开始导入商品数据...")
    success = import_products()
    
    if success:
        logger.info("商品数据导入完成!")
    else:
        logger.error("商品数据导入失败!") 