#!/usr/bin/env python
"""
一键式采集导入脚本：采集商品并直接导入数据库
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
from scraper.scrape_direct import (
    scrape_categories, 
    scrape_products_in_category,
    HEADLESS_MODE
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scrape_import_direct.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 基础配置
BASE_URL = "https://houseofsxn.com"
IMAGES_DIR = "scraped_images"  # 图片保存目录

# 测试模式配置
TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() in ('true', '1', 't')
MAX_CATEGORIES = 2 if TEST_MODE else None  # 测试模式下最多处理的分类数量

# 确保图片保存目录存在
Path(IMAGES_DIR).mkdir(exist_ok=True, parents=True)

# 统计计数器
stats = {
    'categories_found': 0,
    'categories_imported': 0,
    'products_found': 0,
    'products_imported': 0,
    'products_updated': 0,
    'products_skipped': 0,
    'images_found': 0,
    'images_imported': 0
}

# 定义同步版本的函数
def import_category_sync(category_data, category_map=None):
    """导入单个分类（同步版本）"""
    if category_map is None:
        category_map = {}
    
    category_name = category_data['name']
    parent_name = category_data.get('parent', None)
    
    try:
        # 检查分类是否已经存在
        category, created = GoodsCategory.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'从{BASE_URL}采集的分类',
                'level': 1,
                'is_active': True,
                'sort_order': 0
            }
        )
        
        # 记录分类ID映射
        category_map[category_name] = category.id
        
        if created:
            logger.info(f"新建分类: {category_name} (ID: {category.id})")
        else:
            logger.info(f"分类已存在: {category_name} (ID: {category.id})")
        
        # 返回分类对象和映射
        return category, category_map, created
    
    except Exception as e:
        logger.error(f"导入分类 '{category_name}' 失败: {e}")
        traceback.print_exc()
        return None, category_map, False

# 使用sync_to_async包装同步函数
import_category = sync_to_async(import_category_sync)

def set_parent_categories_sync(category_map, categories):
    """设置分类的父子关系（同步版本）"""
    for category_data in categories:
        category_name = category_data['name']
        parent_name = category_data.get('parent', None)
        
        if parent_name and parent_name in category_map and category_name in category_map:
            try:
                category = GoodsCategory.objects.get(id=category_map[category_name])
                parent_category = GoodsCategory.objects.get(id=category_map[parent_name])
                
                # 设置父分类
                category.parent_category = parent_category
                category.save()
                
                logger.info(f"设置分类 '{category_name}' 的父分类为 '{parent_name}'")
            
            except Exception as e:
                logger.error(f"设置分类 '{category_name}' 的父分类关系失败: {e}")

# 使用sync_to_async包装同步函数
set_parent_categories = sync_to_async(set_parent_categories_sync)

def import_product_sync(product_data, category_map):
    """导入单个商品（同步版本）"""
    title = product_data.get('title', '')
    category_name = product_data.get('category', '')
    parent_category_name = product_data.get('parent_category', '')
    
    # 如果没有标题，跳过导入
    if not title:
        logger.warning(f"跳过导入商品: 标题为空")
        return None, False, False, 0
    
    # 获取分类ID
    category_id = None
    if category_name in category_map:
        category_id = category_map[category_name]
    elif parent_category_name in category_map:
        # 如果找不到直接分类，尝试使用父分类
        category_id = category_map[parent_category_name]
        logger.info(f"未找到分类 '{category_name}'，使用父分类 '{parent_category_name}'")
    
    if not category_id:
        logger.warning(f"跳过导入商品 '{title}': 未找到对应的分类ID")
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
    
    try:
        # 检查商品是否已存在
        try:
            # 先通过source_url查找
            goods = Goods.objects.get(source_url=source_url)
            created = False
            logger.info(f"通过source_url找到已存在商品: {title}")
        except Goods.DoesNotExist:
            # 再通过名称和分类查找
            try:
                goods = Goods.objects.get(name=title, category_id=category_id)
                created = False
                logger.info(f"通过名称和分类找到已存在商品: {title}")
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
        goods.original_price = price  # 可以设置原价等于售价，或者稍高一些
        goods.source_url = source_url
        goods.status = 'published' if is_on_sale else 'off_shelf'
        goods.is_recommended = True  # 新导入的商品设为推荐
        goods.is_hot = is_on_sale
        goods.is_new = True
        goods.stock = 100  # 所有商品统一设置库存为100
        
        # 保存商品
        goods.save()
        
        # 处理商品图片
        images_imported = 0
        if local_images:
            # 优先使用本地图片，确保已下载到本地
            for i, img_path in enumerate(local_images):
                if os.path.exists(img_path):
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
                        logger.info(f"为商品 '{title}' 添加图片: {img_path}")
                        images_imported += 1
        elif images:
            # 如果没有本地图片，使用远程图片URL
            for i, img_url in enumerate(images):
                # 提取图片文件名，去掉域名和查询参数
                img_filename = img_url.split('/')[-1].split('?')[0]
                img_category_dir = title.lower().replace(' ', '-')
                
                # 构建正确的相对路径 - 不要包含完整URL
                relative_path = f"{img_category_dir}/{img_filename}"
                
                # 创建图片对象 - 使用相对路径格式
                image, img_created = GoodsImage.objects.get_or_create(
                    goods=goods,
                    image=relative_path,
                    defaults={
                        'is_main': i == 0,  # 第一张图设为主图
                        'sort_order': i
                    }
                )
                
                if img_created:
                    logger.info(f"为商品 '{title}' 添加远程图片: {img_url} -> {relative_path}")
                    images_imported += 1
        
        # 设置主图
        if not goods.image and images:
            img_url = images[0]
            img_filename = img_url.split('/')[-1].split('?')[0]
            img_category_dir = title.lower().replace(' ', '-')
            
            # 同样使用相对路径作为主图
            goods.image = f"{img_category_dir}/{img_filename}"
            goods.save(update_fields=['image'])
        
        if created:
            logger.info(f"新建商品: {title} (ID: {goods.id})")
        else:
            logger.info(f"更新商品: {title} (ID: {goods.id})")
        
        return goods, created, True, images_imported
    
    except Exception as e:
        logger.error(f"导入商品 '{title}' 失败: {e}")
        traceback.print_exc()
        return None, False, False, 0

# 使用sync_to_async包装同步函数
import_product = sync_to_async(import_product_sync)

async def main():
    """主函数: 采集并导入所有分类和商品"""
    start_time = datetime.now()
    
    logger.info("=== 开始采集并导入任务 ===")
    logger.info(f"采集目标网站: {BASE_URL}")
    if TEST_MODE:
        logger.info("运行在测试模式，将仅处理有限的分类和商品")
    logger.info(f"浏览器模式: {'无头模式' if HEADLESS_MODE else '可视模式'}")
    
    print("\n🚀 开始采集并导入数据...")
    print(f"🔍 采集目标: {BASE_URL}")
    if TEST_MODE:
        print("⚠️ 测试模式: 仅处理有限的数据")
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS_MODE)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        # 采集所有分类
        categories = await scrape_categories(page)
        stats['categories_found'] = len(categories)
        logger.info(f"共找到 {len(categories)} 个分类")
        print(f"📊 共找到 {len(categories)} 个分类")
        
        # 在测试模式下限制分类数量
        if TEST_MODE and MAX_CATEGORIES and len(categories) > MAX_CATEGORIES:
            categories = categories[:MAX_CATEGORIES]
            logger.info(f"测试模式: 限制为前 {len(categories)} 个分类")
            print(f"⚠️ 测试模式: 仅处理前 {len(categories)} 个分类")
        
        # 导入分类
        category_map = {}  # 用于存储分类名称到ID的映射
        
        print("\n📁 第一步: 导入分类...")
        for i, category in enumerate(categories, 1):
            print(f"  处理分类 ({i}/{len(categories)}): {category['name']}")
            category_obj, category_map, created = await import_category(category, category_map)
            
            if created:
                stats['categories_imported'] += 1
        
        # 设置分类的父子关系
        await set_parent_categories(category_map, categories)
        
        # 采集并导入每个分类中的商品
        print("\n🛍️ 第二步: 采集并导入商品...")
        for i, category in enumerate(categories, 1):
            category_name = category['name']
            print(f"\n⏳ 正在处理分类 ({i}/{len(categories)}): {category_name}")
            
            # 采集分类中的商品
            category_products = await scrape_products_in_category(page, category)
            stats['products_found'] += len(category_products)
            stats['images_found'] += sum(len(product.get('images', [])) for product in category_products)
            
            logger.info(f"分类 '{category_name}' 中找到 {len(category_products)} 个商品")
            print(f"📊 分类 '{category_name}' 中找到 {len(category_products)} 个商品")
            
            # 导入商品
            products_imported = 0
            products_updated = 0
            products_skipped = 0
            images_imported = 0
            for j, product in enumerate(category_products, 1):
                product_title = product.get('title', f'未知商品 {j}')
                print(f"  处理商品 ({j}/{len(category_products)}): {product_title}")
                
                # 导入商品
                goods_obj, created, success, img_count = await import_product(product, category_map)
                
                if success:
                    if created:
                        products_imported += 1
                        stats['products_imported'] += 1
                    else:
                        products_updated += 1
                        stats['products_updated'] += 1
                    
                    # 更新导入的图片数
                    images_imported += img_count
                    stats['images_imported'] += img_count
                else:
                    products_skipped += 1
                    stats['products_skipped'] += 1
            
            logger.info(f"分类 '{category_name}' 导入结果: 新增 {products_imported} 个, 更新 {products_updated} 个, 跳过 {products_skipped} 个")
            print(f"✅ 分类 '{category_name}' 导入结果: 新增 {products_imported} 个, 更新 {products_updated} 个, 跳过 {products_skipped} 个")
        
        await browser.close()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=== 采集并导入任务完成! ===")
    logger.info(f"统计信息:")
    logger.info(f"- 分类: 发现 {stats['categories_found']} 个, 导入 {stats['categories_imported']} 个")
    logger.info(f"- 商品: 发现 {stats['products_found']} 个, 导入 {stats['products_imported']} 个, 更新 {stats['products_updated']} 个, 跳过 {stats['products_skipped']} 个")
    logger.info(f"- 图片: 发现 {stats['images_found']} 张, 导入 {stats['images_imported']} 张")
    logger.info(f"- 耗时: {duration:.2f} 秒")
    
    print(f"\n🎉 采集并导入任务完成!")
    print(f"📊 统计信息:")
    print(f"  - 分类: 发现 {stats['categories_found']} 个, 导入 {stats['categories_imported']} 个")
    print(f"  - 商品: 发现 {stats['products_found']} 个, 导入 {stats['products_imported']} 个, 更新 {stats['products_updated']} 个, 跳过 {stats['products_skipped']} 个")
    print(f"  - 图片: 发现 {stats['images_found']} 张, 导入 {stats['images_imported']} 张")
    print(f"  - 耗时: {duration//60:.0f} 分 {duration%60:.0f} 秒")
    
    return True

if __name__ == "__main__":
    asyncio.run(main()) 