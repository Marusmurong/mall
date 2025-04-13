#!/usr/bin/env python
"""
DrHarness采集数据导入脚本：将采集到的商品导入数据库（新版）
"""
import os
import sys
import json
import asyncio
import logging
import django
import traceback
from datetime import datetime
from pathlib import Path
from asgiref.sync import sync_to_async

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入Django模型
from goods.models import GoodsCategory, Goods, GoodsImage
from scraper.scrape_yeezysupply import (
    get_all_products, 
    scrape_product_details,
    HEADLESS_MODE
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("drharness_new_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 基础配置
BASE_URL = "https://drharness.co"
IMAGES_DIR = "scraped_images/drharness_new"  # 图片保存目录

# 测试模式配置
TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() in ('true', '1', 't')
MAX_PRODUCTS = 5 if TEST_MODE else None  # 测试模式下最多处理的商品数量

# 确保图片保存目录存在
Path(IMAGES_DIR).mkdir(exist_ok=True, parents=True)

# 统计计数器
stats = {
    'products_found': 0,
    'products_imported': 0,
    'products_updated': 0,
    'products_skipped': 0,
    'images_found': 0,
    'images_imported': 0
}

# 确保鞋类分类存在
def ensure_category_sync():
    """确保Leather分类存在（同步版本）"""
    try:
        # 检查分类是否已经存在
        category, created = GoodsCategory.objects.get_or_create(
            name="Leather Bondage",
            defaults={
                'description': '皮革束缚系列产品',
                'level': 1,
                'is_active': True,
                'sort_order': 0
            }
        )
        
        if created:
            logger.info(f"新建分类: Leather Bondage (ID: {category.id})")
        else:
            logger.info(f"分类已存在: Leather Bondage (ID: {category.id})")
        
        return category.id
    
    except Exception as e:
        logger.error(f"创建Leather Bondage分类失败: {e}")
        traceback.print_exc()
        return None

# 使用sync_to_async包装同步函数
ensure_category = sync_to_async(ensure_category_sync)

def import_product_sync(product_data, category_id):
    """导入单个商品（同步版本）"""
    title = product_data.get('title', '')
    
    # 如果没有标题，跳过导入
    if not title:
        logger.warning(f"跳过导入商品: 标题为空")
        return None, False, False, 0
    
    # 获取价格信息
    price = 0
    if 'price_usd' in product_data and product_data['price_usd']:
        price = float(product_data['price_usd'])
    elif 'price_original' in product_data and product_data['price_original']:
        price = float(product_data['price_original'])
    
    # 获取商品描述
    description = product_data.get('description', '')
    
    # 获取商品URL
    source_url = product_data.get('url', '')
    
    # 获取商品状态
    is_on_sale = product_data.get('in_stock', True)
    
    # 获取商品图片
    images = product_data.get('images', [])
    local_images = product_data.get('local_images', [])
    main_image = product_data.get('main_image', '')
    
    # 获取SKU
    sku = product_data.get('sku', '')
    
    try:
        # 检查商品是否已存在
        try:
            # 先通过source_url查找
            goods = Goods.objects.get(source_url=source_url)
            created = False
            logger.info(f"通过source_url找到已存在商品: {title}")
        except Goods.DoesNotExist:
            # 再通过名称查找
            try:
                goods = Goods.objects.get(name=title)
                created = False
                logger.info(f"通过名称找到已存在商品: {title}")
            except Goods.DoesNotExist:
                # 创建新商品
                goods = Goods()
                created = True
        
        # 更新或创建商品信息
        goods.name = title
        goods.category_id = category_id
        goods.description = description
        goods.goods_desc = description  # 使用相同的描述信息
        goods.price = price
        goods.original_price = price  # 可以设置原价等于售价
        goods.source_url = source_url
        goods.goods_sn = sku  # 使用产品SKU作为商品编号
        goods.status = 'published' if is_on_sale else 'off_shelf'
        goods.is_recommended = True  # 新导入的商品设为推荐
        goods.is_hot = is_on_sale
        goods.is_new = True
        goods.stock = 100 if is_on_sale else 0  # 假设有库存为100，无库存为0
        
        # 保存商品基本信息
        goods.save()
        
        if created:
            logger.info(f"成功创建新商品: {title}")
            stats['products_imported'] += 1
        else:
            logger.info(f"成功更新商品: {title}")
            stats['products_updated'] += 1
        
        # 处理商品图片
        imported_images = 0
        for i, img_path in enumerate(local_images):
            try:
                # 创建图片对象
                image, img_created = GoodsImage.objects.get_or_create(
                    goods=goods,
                    image=img_path.replace('scraped_images/', ''),
                    defaults={
                        'is_main': i == 0,  # 第一张图设为主图
                        'sort_order': i
                    }
                )
                
                if img_created:
                    logger.info(f"为商品 {title} 添加图片: {img_path}")
                    imported_images += 1
                    stats['images_imported'] += 1
                else:
                    logger.info(f"商品 {title} 图片已存在: {img_path}")
            
            except Exception as e:
                logger.error(f"导入商品 {title} 的图片失败: {e}")
        
        # 设置商品主图
        if not goods.image and local_images:
            goods.image = local_images[0].replace('scraped_images/', '')
            goods.save(update_fields=['image'])
            logger.info(f"设置商品 {title} 的主图: {goods.image}")
        
        return goods, created, True, imported_images
    
    except Exception as e:
        logger.error(f"导入商品 '{title}' 失败: {e}")
        traceback.print_exc()
        return None, False, False, 0

# 使用sync_to_async包装同步函数
import_product = sync_to_async(import_product_sync)

async def main():
    """主函数: 采集并导入DrHarness商品（新版）"""
    start_time = datetime.now()
    
    logger.info("=== 开始采集并导入DrHarness商品（新版） ===")
    logger.info(f"采集目标网站: {BASE_URL}")
    if TEST_MODE:
        logger.info("运行在测试模式，将仅处理有限的商品")
    
    # 导入商品前需确保分类存在
    category_id = await ensure_category()
    if not category_id:
        logger.error("无法创建分类，导入中止")
        return
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS_MODE)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        # 获取所有商品基本信息
        products_info = await get_all_products(page)
        stats['products_found'] = len(products_info)
        logger.info(f"共找到 {len(products_info)} 个商品")
        
        # 如果在测试模式下，只获取部分商品
        if TEST_MODE and MAX_PRODUCTS and len(products_info) > MAX_PRODUCTS:
            logger.info(f"测试模式: 只处理前 {MAX_PRODUCTS} 个商品")
            products_info = products_info[:MAX_PRODUCTS]
        
        # 采集并导入每个商品
        for i, product_info in enumerate(products_info, 1):
            logger.info(f"正在处理商品 ({i}/{len(products_info)}): {product_info.get('title', 'Unknown')}")
            
            # 采集商品详情
            product_data = await scrape_product_details(page, product_info)
            
            if product_data:
                # 图片数量统计
                stats['images_found'] += len(product_data.get('local_images', []))
                
                # 导入商品到数据库
                goods, created, success, imported_images = await import_product(product_data, category_id)
                
                if success:
                    logger.info(f"成功{'创建' if created else '更新'}商品: {product_data['title']}")
                else:
                    logger.warning(f"导入商品失败: {product_data.get('title', 'Unknown')}")
                    stats['products_skipped'] += 1
            else:
                logger.warning(f"无法采集商品详情: {product_info.get('title', 'Unknown')}")
                stats['products_skipped'] += 1
            
            # 添加短暂延迟，避免请求过快
            await asyncio.sleep(2)
        
        await browser.close()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=== DrHarness商品采集和导入完成（新版）! ===")
    logger.info(f"统计信息:")
    logger.info(f"- 发现商品: {stats['products_found']} 个")
    logger.info(f"- 导入新商品: {stats['products_imported']} 个")
    logger.info(f"- 更新商品: {stats['products_updated']} 个")
    logger.info(f"- 跳过商品: {stats['products_skipped']} 个")
    logger.info(f"- 发现图片: {stats['images_found']} 张")
    logger.info(f"- 导入图片: {stats['images_imported']} 张")
    logger.info(f"- 总耗时: {duration:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main()) 