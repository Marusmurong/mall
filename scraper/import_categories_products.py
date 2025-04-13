#!/usr/bin/env python
"""
导入脚本：将采集的分类和商品数据导入到Django数据库
"""
import os
import sys
import json
import logging
import django
from decimal import Decimal
from pathlib import Path
from django.core.files.base import ContentFile
import requests
from urllib.parse import urlparse
from io import BytesIO
from django.utils.text import slugify
import time

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
        logging.FileHandler(os.path.join(BASE_DIR, "import_data.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 采集数据文件
SCRAPED_DATA_FILE = os.path.join(BASE_DIR, "scraped_categories_products.json")

def load_scraped_data():
    """加载采集的数据"""
    try:
        with open(SCRAPED_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"成功加载采集数据，共 {data.get('total_categories', 0)} 个分类和 {data.get('total_products', 0)} 个商品")
        return data
    except Exception as e:
        logger.error(f"加载采集数据失败: {e}")
        return None

def download_image(url):
    """从URL下载图片并返回内容"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            logger.error(f"下载图片失败, 状态码: {response.status_code}, URL: {url}")
            return None
    except Exception as e:
        logger.error(f"下载图片异常: {e}, URL: {url}")
        return None

def get_filename_from_url(url):
    """从URL中获取文件名"""
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)
    # 如果文件名中没有扩展名，添加.jpg
    if '.' not in filename:
        filename = f"{filename}.jpg"
    return filename

def import_categories(categories_data):
    """导入商品分类"""
    category_map = {}  # 用于存储类别名称与数据库ID的映射
    parent_map = {}    # 用于存储类别的父子关系
    
    try:
        # 第一次遍历：创建所有分类
        for category_data in categories_data:
            name = category_data.get('name')
            url = category_data.get('url')
            parent_name = category_data.get('parent')
            
            if not name:
                continue
            
            # 查找或创建分类
            category, created = GoodsCategory.objects.get_or_create(
                name=name,
                defaults={
                    'level': 1 if not parent_name else 2,  # 如果有父级，则为2级分类
                    'description': f'从 {url} 采集的分类',
                    'is_active': True
                }
            )
            
            if created:
                logger.info(f"创建新分类: {name}")
            else:
                logger.info(f"更新已有分类: {name}")
            
            # 存储类别映射和父子关系
            category_map[name] = category.id
            if parent_name:
                parent_map[name] = parent_name
        
        # 第二次遍历：设置父子关系
        for child_name, parent_name in parent_map.items():
            if parent_name in category_map and child_name in category_map:
                child_id = category_map[child_name]
                parent_id = category_map[parent_name]
                
                # 更新子分类的父级
                child_category = GoodsCategory.objects.get(id=child_id)
                parent_category = GoodsCategory.objects.get(id=parent_id)
                
                child_category.parent = parent_category
                child_category.level = parent_category.level + 1
                child_category.save()
                
                logger.info(f"设置分类关系: {child_name} -> {parent_name}")
        
        return category_map
    
    except Exception as e:
        logger.error(f"导入分类失败: {e}")
        return {}

def import_products(products_data, category_map):
    """导入商品数据
    
    参数:
        products_data: 商品数据列表
        category_map: 类目名称到ID的映射
    
    返回:
        (created_count, updated_count, skipped_count) 创建、更新和跳过的商品数量
    """
    if not products_data:
        logger.warning("没有商品数据可导入")
        return 0, 0, 0
    
    # 导入Django模型
    from goods.models import Goods, GoodsImage, GoodsCategory
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    duplicated_count = 0
    
    # 获取已存在的商品URL集合，用于快速检查重复
    existing_urls = set(Goods.objects.values_list('source_url', flat=True))
    logger.info(f"数据库中已有 {len(existing_urls)} 个商品")
    
    # 创建一个集合记录当前批次已处理的URL，避免同一批次中的重复
    processed_urls = set()
    
    for product in products_data:
        try:
            # 获取必要的商品信息
            title = product.get('title', '')
            url = product.get('url', '')
            
            # 如果URL为空，跳过
            if not url:
                logger.warning(f"商品缺少URL，跳过: {title}")
                skipped_count += 1
                continue
            
            # 检查是否是当前批次已处理的商品
            if url in processed_urls:
                logger.info(f"当前批次中的重复商品，跳过: {title} ({url})")
                duplicated_count += 1
                continue
            else:
                processed_urls.add(url)
            
            # 获取其他信息
            description = product.get('description', '')
            price_original = product.get('price_original', 0)
            currency_original = product.get('currency_original', 'USD')
            price_usd = product.get('price_usd', 0)
            sku = product.get('sku', '')
            brand = product.get('brand', '')
            in_stock = product.get('in_stock', True)
            category_name = product.get('category', '')
            parent_category_name = product.get('parent_category', '')
            
            # 查找对应的类目
            category_id = None
            if category_name and category_name in category_map:
                category_id = category_map[category_name]
            elif parent_category_name and parent_category_name in category_map:
                # 如果找不到直接类目，尝试使用父类目
                category_id = category_map[parent_category_name]
                logger.info(f"商品 '{title}' 使用父类目 '{parent_category_name}'")
            
            if not category_id:
                logger.warning(f"商品 '{title}' 没有找到对应的类目，跳过")
                skipped_count += 1
                continue
            
            # 查找该商品是否已存在
            existing_product = None
            if url in existing_urls:
                try:
                    existing_product = Goods.objects.get(source_url=url)
                    logger.debug(f"找到已存在的商品: {title}")
                except Goods.DoesNotExist:
                    pass
            
            if existing_product:
                # 更新已存在的商品
                existing_product.name = title
                existing_product.goods_brief = title
                existing_product.goods_desc = description
                existing_product.goods_front_image = product.get('main_image', '')
                
                # 更新价格
                if price_usd > 0:
                    existing_product.shop_price = price_usd
                elif price_original > 0:
                    existing_product.shop_price = price_original
                
                # 更新库存状态
                existing_product.is_new = True  # 标记为新品
                existing_product.is_hot = True  # 标记为热销
                existing_product.goods_num = 100 if in_stock else 0  # 设置库存数量
                
                # 保存更新
                existing_product.save()
                updated_count += 1
                logger.info(f"更新商品: {title}")
                
                # 处理商品图片
                main_image = product.get('main_image', '')
                images = product.get('images', [])
                local_images = product.get('local_images', [])
                
                # 如果有本地图片，优先使用本地图片
                if local_images:
                    logger.info(f"商品 '{title}' 有 {len(local_images)} 张本地图片")
                    # 检查是否需要添加新图片
                    existing_images = set(existing_product.images.values_list('image', flat=True))
                    for local_img_path in local_images:
                        if local_img_path not in existing_images:
                            # 创建图片记录
                            img = GoodsImage(goods=existing_product, image=local_img_path)
                            img.save()
                            logger.debug(f"添加本地图片: {local_img_path}")
                
            else:
                # 创建新商品
                category = GoodsCategory.objects.get(id=category_id)
                
                # 设置价格
                shop_price = 0
                if price_usd > 0:
                    shop_price = price_usd
                elif price_original > 0:
                    shop_price = price_original
                
                # 创建商品对象
                new_product = Goods(
                    category=category,
                    name=title,
                    goods_sn=sku or f"SN{int(time.time())}",
                    click_num=0,
                    sold_num=0,
                    fav_num=0,
                    goods_num=100 if in_stock else 0,  # 设置库存数量
                    market_price=shop_price * 1.2,  # 市场价略高于售价
                    shop_price=shop_price,
                    goods_brief=title,
                    goods_desc=description,
                    ship_free=True,
                    goods_front_image=product.get('main_image', ''),
                    is_new=True,  # 标记为新品
                    is_hot=True,  # 标记为热销
                    source_url=url  # 保存来源URL
                )
                
                # 保存商品
                new_product.save()
                created_count += 1
                logger.info(f"创建商品: {title}")
                
                # 处理商品图片
                main_image = product.get('main_image', '')
                images = product.get('images', [])
                local_images = product.get('local_images', [])
                
                # 如果有本地图片，优先使用本地图片
                if local_images:
                    logger.info(f"商品 '{title}' 有 {len(local_images)} 张本地图片")
                    for local_img_path in local_images:
                        # 创建图片记录
                        img = GoodsImage(goods=new_product, image=local_img_path)
                        img.save()
                        logger.debug(f"添加本地图片: {local_img_path}")
                elif images:
                    # 如果没有本地图片但有在线图片，使用在线图片
                    logger.info(f"商品 '{title}' 有 {len(images)} 张在线图片")
                    for img_url in images:
                        if img_url:
                            img = GoodsImage(goods=new_product, image=img_url)
                            img.save()
                            logger.debug(f"添加在线图片: {img_url}")
        
        except Exception as e:
            logger.error(f"导入商品时出错: {e}")
            skipped_count += 1
            continue
    
    logger.info(f"商品导入完成: 新建 {created_count}, 更新 {updated_count}, 跳过 {skipped_count}, 重复 {duplicated_count}")
    return created_count, updated_count, skipped_count

def import_data(scraped_data):
    """导入采集的数据到数据库
    
    参数:
        scraped_data: 包含categories和products的字典数据
    
    返回:
        包含导入结果统计的字典
    """
    logger.info("=== 开始导入数据 ===")
    print("\n📥 开始导入数据到数据库...")
    
    # 提取分类和商品数据
    categories = scraped_data.get('categories', [])
    products = scraped_data.get('products', [])
    
    logger.info(f"准备导入 {len(categories)} 个分类和 {len(products)} 个商品")
    print(f"📊 准备导入 {len(categories)} 个分类和 {len(products)} 个商品")
    
    # 导入分类
    print("⏳ 正在导入分类...")
    category_map = import_categories(categories)
    logger.info(f"已导入 {len(category_map)} 个分类")
    print(f"✅ 成功导入 {len(category_map)} 个分类")
    
    # 导入商品
    print("⏳ 正在导入商品...")
    total_created, total_updated, total_skipped = import_products(products, category_map)
    
    # 导入结果统计
    result = {
        'categories': {
            'total': len(categories),
            'imported': len(category_map)
        },
        'products': {
            'total': len(products),
            'created': total_created,
            'updated': total_updated,
            'skipped': total_skipped
        }
    }
    
    logger.info(f"=== 数据导入完成 ===")
    logger.info(f"分类: 总数 {len(categories)}, 导入 {len(category_map)}")
    logger.info(f"商品: 总数 {len(products)}, 新建 {total_created}, 更新 {total_updated}, 跳过 {total_skipped}")
    
    print("\n🎉 数据导入完成!")
    print(f"📊 导入统计:")
    print(f"  - 分类: 总数 {len(categories)}, 成功导入 {len(category_map)}")
    print(f"  - 商品: 总数 {len(products)}")
    print(f"    + 新建: {total_created} 个")
    print(f"    + 更新: {total_updated} 个")
    print(f"    + 跳过: {total_skipped} 个")
    
    return result

if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
    import django
    django.setup()
    
    # 从文件加载数据
    from scraper.scrape_direct import RESULTS_FILE
    
    if not os.path.exists(RESULTS_FILE):
        logger.error(f"采集数据文件不存在: {RESULTS_FILE}")
        sys.exit(1)
    
    # 加载采集的数据
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
            
        # 导入数据
        result = import_data(scraped_data)
        print(f"导入完成! 结果: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        logger.error(f"导入过程出错: {e}")
        raise 