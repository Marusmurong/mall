#!/usr/bin/env python
"""
测试脚本：测试采集的商品数据并导入到Django数据库
"""
import os
import sys
import json
import logging
import django
from django.core.files import File
from decimal import Decimal
from pathlib import Path

# 将项目根目录添加到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入Django模型
from goods.models import Goods, GoodsCategory, GoodsImage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "import.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 采集数据文件和图片目录
SCRAPED_DATA_FILE = os.path.join(BASE_DIR, "scraped_products.json")
SCRAPED_IMAGES_DIR = os.path.join(BASE_DIR, "scraped_images")

def load_scraped_data():
    """加载采集的数据"""
    try:
        with open(SCRAPED_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"成功加载采集数据，共 {len(data)} 条商品记录")
        return data
    except Exception as e:
        logger.error(f"加载采集数据失败: {e}")
        return []

def get_or_create_category():
    """获取或创建商品分类"""
    # 这里为采集的商品创建一个默认分类，实际项目中可以根据需要调整
    category, created = GoodsCategory.objects.get_or_create(
        name="BDSM用品",
        defaults={
            'level': 1,
            'description': '采集自houseofsxn.com的BDSM用品',
        }
    )
    if created:
        logger.info(f"创建新分类: {category.name}")
    else:
        logger.info(f"使用已有分类: {category.name}")
    return category

def import_product(product_data, category):
    """导入单个商品数据"""
    try:
        # 检查商品是否已存在（基于source_url）
        existing_product = Goods.objects.filter(source_url=product_data['source_url']).first()
        if existing_product:
            logger.info(f"商品已存在，跳过导入: {product_data['title']}")
            return None
        
        # 处理价格
        try:
            price = Decimal(product_data['price'])
        except:
            price = Decimal('0.00')
            logger.warning(f"价格格式有误，使用默认价格0: {product_data['title']}")

        # 创建商品记录
        product = Goods.objects.create(
            name=product_data['title'],
            category=category,
            price=price,
            original_price=price,  # 可以根据需要设置不同价格
            stock=10,  # 设置默认库存
            description=product_data['description'][:500] if len(product_data['description']) > 500 else product_data['description'],
            goods_desc=product_data['description'],
            source_url=product_data['source_url'],
            status='published',  # 设置为已发布状态
            is_new=True
        )
        
        logger.info(f"成功创建商品: {product.name}")
        
        # 导入商品图片
        if product_data['images']:
            for i, img_name in enumerate(product_data['images']):
                img_path = os.path.join(SCRAPED_IMAGES_DIR, img_name)
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as img_file:
                        # 创建商品图片记录
                        goods_image = GoodsImage(
                            goods=product,
                            is_main=(i == 0),  # 第一张设为主图
                            sort_order=i
                        )
                        goods_image.image.save(img_name, File(img_file))
                        logger.info(f"已导入图片 {i+1}/{len(product_data['images'])}: {img_name}")
                else:
                    logger.warning(f"图片文件不存在: {img_path}")
        
        # 确保主图设置正确
        product.refresh_from_db()
        # 由于Goods模型的save方法已经会处理主图，这里不需要额外操作
        
        return product
    
    except Exception as e:
        logger.error(f"导入商品失败: {product_data['title']}, 错误: {e}")
        return None

def main():
    """主函数：测试采集数据并导入数据库"""
    try:
        logger.info("=== 开始测试导入采集数据 ===")
        
        # 检查采集数据文件是否存在
        if not os.path.exists(SCRAPED_DATA_FILE):
            logger.error(f"采集数据文件不存在: {SCRAPED_DATA_FILE}")
            return
        
        # 检查图片目录是否存在
        if not os.path.exists(SCRAPED_IMAGES_DIR):
            logger.error(f"图片目录不存在: {SCRAPED_IMAGES_DIR}")
            return
        
        # 加载采集数据
        products_data = load_scraped_data()
        if not products_data:
            logger.error("没有可导入的商品数据")
            return
        
        # 获取或创建商品分类
        category = get_or_create_category()
        
        # 导入商品数据
        success_count = 0
        for i, product_data in enumerate(products_data, 1):
            logger.info(f"正在导入第 {i}/{len(products_data)} 个商品: {product_data['title']}")
            product = import_product(product_data, category)
            if product:
                success_count += 1
        
        logger.info("=== 导入完成 ===")
        logger.info(f"共导入 {success_count}/{len(products_data)} 个商品")
    
    except Exception as e:
        logger.error(f"导入过程中发生错误: {e}")

if __name__ == "__main__":
    main() 