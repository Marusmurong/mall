#!/usr/bin/env python
import os
import sys
import django
import glob
from pathlib import Path
import argparse
import time
import json
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入模型
from goods.models import Goods, GoodsCategory, GoodsImage
from django.db import transaction
from django.core.files.base import ContentFile
import decimal
import re

# 导入智能导入脚本
from smart_import import import_batch, get_batch_files, extract_short_description

def get_unique_products(batch_file, existing_urls=None, limit=None):
    """获取不重复的商品"""
    if existing_urls is None:
        existing_urls = set()
    
    # 加载批次文件
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
        return []
    
    # 提取产品
    products = data.get('products', [])
    if not products:
        return []
    
    # 过滤已存在的产品
    unique_products = []
    for product in products:
        source_url = product.get('source_url', '')
        if source_url and source_url not in existing_urls:
            unique_products.append(product)
            existing_urls.add(source_url)
            if limit and len(unique_products) >= limit:
                break
    
    return unique_products

def direct_import_batch(batch_file, existing_urls=None, limit=None, category_name=None):
    """直接导入批次文件，不使用smart_import的函数"""
    if existing_urls is None:
        existing_urls = set()
    
    # 获取不重复的商品
    products = get_unique_products(batch_file, existing_urls, limit)
    
    print(f"找到 {len(products)} 个不重复商品")
    if not products:
        return 0, 0
    
    # 导入商品
    imported_count = 0
    error_count = 0
    
    for product in products:
        try:
            with transaction.atomic():
                # 确定分类
                from category_mapping import determine_category
                product_category = determine_category(
                    product['title'], 
                    category_name=category_name, 
                    batch_filename=batch_file.name
                )
                
                # 获取或创建分类
                top_category = None
                second_category = None
                third_category = None
                
                # 获取顶级分类
                if len(product_category) > 0:
                    top_category, _ = GoodsCategory.objects.get_or_create(
                        name=product_category[0],
                        defaults={
                            'level': 1,
                            'description': f'{product_category[0]} category'
                        }
                    )
                
                # 获取二级分类
                if len(product_category) > 1 and top_category:
                    second_category, _ = GoodsCategory.objects.get_or_create(
                        name=product_category[1],
                        defaults={
                            'level': 2,
                            'parent': top_category,
                            'description': f'{product_category[1]} subcategory'
                        }
                    )
                
                # 获取三级分类
                if len(product_category) > 2 and second_category:
                    third_category, _ = GoodsCategory.objects.get_or_create(
                        name=product_category[2],
                        defaults={
                            'level': 3,
                            'parent': second_category,
                            'description': f'{product_category[2]} subcategory'
                        }
                    )
                
                # 使用最后一级分类
                target_category = third_category or second_category or top_category
                if not target_category:
                    # 默认使用"Home Life"分类
                    target_category, _ = GoodsCategory.objects.get_or_create(
                        name="Home Life",
                        defaults={
                            'level': 1,
                            'description': 'Home lifestyle products and accessories'
                        }
                    )
                
                # 提取价格并转换为小数
                price_str = product.get('price', '')
                if not price_str or price_str.strip() == '':
                    price = decimal.Decimal('19.99')  # 设置默认价格
                else:
                    price_str = price_str.replace('$', '')
                    # 确保移除所有非数字字符(除了小数点)
                    price_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
                    price = decimal.Decimal(price_str) if price_str else decimal.Decimal('19.99')
                
                # 截断标题，确保不超过200个字符
                title = product['title']
                if len(title) > 200:
                    title = title[:197] + "..."
                
                # 检查是否已存在相同URL的商品
                if Goods.objects.filter(source_url=product.get('source_url', '')[:500]).exists():
                    continue
                
                # 创建商品记录
                goods = Goods(
                    name=title,
                    category=target_category,
                    price=price,
                    original_price=price * decimal.Decimal('1.2'),  # 原价设为当前价格的1.2倍
                    stock=100,  # 默认库存为100
                    description=extract_short_description(product.get('description', '')),
                    goods_desc=product.get('description', ''),
                    source_url=product.get('source_url', '')[:500],
                    status='published',  # 直接发布
                    is_recommended=True,
                    is_hot=False,
                    is_new=True,
                )
                goods.save()
                
                # 添加商品图片
                if 'images' in product and product['images']:
                    # 图片基础目录
                    image_dir = Path('/Users/jimmu/mall/scraper/scraped_data/amazon/images')
                    
                    for i, image_name in enumerate(product['images']):
                        # 图片路径
                        image_path = image_dir / image_name
                        
                        # 检查图片是否存在
                        if not image_path.exists():
                            continue
                        
                        # 创建商品图片，只添加前3张图片
                        if i < 3:
                            try:
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
                            except Exception as e:
                                print(f"保存图片时出错: {str(e)}")
                
                imported_count += 1
                
        except Exception as e:
            error_count += 1
            title_preview = product.get('title', 'Unknown')[:100] + '...'
            print(f"导入商品出错: {title_preview}")
            print(f"错误详情: {str(e)}")
    
    return imported_count, error_count

def batch_import_all_unique(start_batch=None, end_batch=None, batch_list=None, total_limit=None, each_batch_limit=None, skip_existing=True, preview=False):
    """
    批量导入多个或所有批次的商品，确保不重复导入
    
    Args:
        start_batch (int): 起始批次号
        end_batch (int): 结束批次号
        batch_list (list): 指定批次号列表
        total_limit (int): 总共导入的商品数量限制
        each_batch_limit (int): 每个批次限制导入的商品数量
        skip_existing (bool): 是否跳过已经存在的商品
        preview (bool): 是否只预览不实际导入
    """
    # 获取数据目录
    data_dir = '/Users/jimmu/mall/scraper/scraped_data/amazon/details'
    
    # 获取所有批次文件
    if batch_list:
        batch_files = []
        for batch_num in batch_list:
            batch_files.extend(get_batch_files(data_dir, batch_num))
    else:
        all_batch_files = sorted(Path(data_dir).glob("amazon_details_batch_*.json"))
        
        if start_batch is not None and end_batch is not None:
            # 根据批次号范围筛选
            batch_files = []
            for batch_file in all_batch_files:
                # 从文件名提取批次号
                try:
                    batch_num = int(batch_file.stem.split('_')[-1])
                    if start_batch <= batch_num <= end_batch:
                        batch_files.append(batch_file)
                except ValueError:
                    continue
        else:
            batch_files = all_batch_files
    
    # 随机打乱批次顺序以获取更多样化的商品
    random.shuffle(batch_files)
    
    total_files = len(batch_files)
    print(f"找到 {total_files} 个批次文件")
    
    if preview:
        print("预览模式：将处理以下批次文件")
        for i, file in enumerate(batch_files[:10], 1):
            print(f"{i}. {file}")
        if len(batch_files) > 10:
            print(f"...等共 {len(batch_files)} 个文件")
        return
    
    # 获取已有商品的URL
    existing_urls = set(Goods.objects.values_list('source_url', flat=True))
    print(f"数据库中已有 {len(existing_urls)} 个商品URL")
    
    # 统计
    start_time = time.time()
    total_imported = 0
    total_errors = 0
    processed_files = 0
    
    for batch_file in batch_files:
        if total_limit and total_imported >= total_limit:
            print(f"已达到总导入数量限制 {total_limit}，停止导入")
            break
            
        processed_files += 1
        progress = processed_files / total_files * 100
        elapsed_time = time.time() - start_time
        
        # 打印进度
        print(f"\n处理文件 {processed_files}/{total_files} ({progress:.1f}%)")
        print(f"已用时间: {elapsed_time:.1f}秒, 预计剩余时间: {(elapsed_time / processed_files * (total_files - processed_files)):.1f}秒")
        
        # 导入批次
        remaining = total_limit - total_imported if total_limit else None
        import_limit = min(each_batch_limit, remaining) if remaining else each_batch_limit
        
        # 使用直接导入函数
        imported, errors = direct_import_batch(
            batch_file, 
            existing_urls=existing_urls, 
            limit=import_limit
        )
        
        total_imported += imported
        total_errors += errors
        
        # 每10个批次显示一次小结
        if processed_files % 10 == 0 or total_imported % 100 == 0:
            print(f"\n小结: 已处理 {processed_files}/{total_files} 个批次, 导入 {total_imported} 个商品, {total_errors} 个错误")
    
    # 总结
    total_time = time.time() - start_time
    print(f"\n导入完成: 共处理 {processed_files} 个批次文件")
    print(f"导入 {total_imported} 个商品, {total_errors} 个错误")
    print(f"总用时: {total_time:.1f}秒, 平均每个批次 {total_time / max(processed_files, 1):.1f}秒")

def main():
    parser = argparse.ArgumentParser(description='批量导入亚马逊商品数据')
    
    # 添加命令行参数
    parser.add_argument('--preview', action='store_true', help='只预览不实际导入')
    parser.add_argument('--start', type=int, help='起始批次号')
    parser.add_argument('--end', type=int, help='结束批次号')
    parser.add_argument('--batches', nargs='+', type=int, help='指定批次号列表（空格分隔）')
    parser.add_argument('--total', type=int, help='总共导入的商品数量')
    parser.add_argument('--limit', type=int, help='每个批次限制导入的商品数量')
    parser.add_argument('--skip-existing', action='store_true', help='跳过已存在的商品')
    
    args = parser.parse_args()
    
    batch_import_all_unique(
        start_batch=args.start,
        end_batch=args.end,
        batch_list=args.batches,
        total_limit=args.total,
        each_batch_limit=args.limit,
        skip_existing=args.skip_existing,
        preview=args.preview
    )

if __name__ == '__main__':
    main() 