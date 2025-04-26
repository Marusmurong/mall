#!/usr/bin/env python
import os
import sys
import json
import decimal
import re
from pathlib import Path
import glob
import django
import argparse
from tqdm import tqdm  # 进度条

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入模型
from goods.models import Goods, GoodsCategory, GoodsImage
from django.core.files.base import ContentFile
from django.db import transaction

# 导入分类映射
from category_mapping import determine_category, CATEGORY_MAPPING

def get_batch_files(directory=None, batch_number=None):
    """
    获取批次文件列表
    
    Args:
        directory (str): 数据目录路径
        batch_number (int): 指定的批次号
    
    Returns:
        list: 批次文件列表
    """
    if not directory:
        directory = '/Users/jimmu/mall/scraper/scraped_data/amazon/details'
    
    directory = Path(directory)
    
    if batch_number:
        # 查找特定批次
        batch_files = list(directory.glob(f"amazon_details_batch_{batch_number}.json"))
    else:
        # 查找所有批次
        batch_files = list(directory.glob("amazon_details_batch_*.json"))
    
    # 按批次号排序
    batch_files.sort()
    return batch_files

def get_category_from_file(batch_file):
    """
    从文件名中提取可能的类别信息
    
    Args:
        batch_file (Path): 批次文件路径
    
    Returns:
        str: 提取的类别名称，如果无法提取则返回None
    """
    # 从文件名中提取类别信息的逻辑
    # 例如: "amazon_details_batch_mugs_1.json" -> "mugs"
    filename = batch_file.name
    match = re.search(r'amazon_details_batch_(\w+)_\d+\.json', filename)
    if match:
        return match.group(1)
    return None

def import_batch(batch_file, preview=False, category_name=None, limit=None):
    """
    导入单个批次文件中的商品
    
    Args:
        batch_file (Path): 批次文件路径
        preview (bool): 是否只预览不实际导入
        category_name (str): 指定的分类名称
        limit (int): 限制导入的商品数量
    
    Returns:
        tuple: (导入成功数量, 错误数量)
    """
    print(f"\n正在处理批次文件: {batch_file}")
    
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
        return 0, 1
    
    # 提取批次中的产品
    products = data.get('products', [])
    if limit:
        products = products[:limit]
    
    print(f"找到 {len(products)} 个商品")
    
    if preview:
        print("\n=== 预览模式 ===")
        for i, product in enumerate(products[:10], 1):  # 只预览前10个
            title = product['title'][:80] + '...' if len(product['title']) > 80 else product['title']
            price = product.get('price', 'N/A')
            image_count = len(product.get('images', []))
            
            # 确定分类
            batch_category = get_category_from_file(batch_file)
            product_category = determine_category(
                product['title'], 
                category_name=category_name, 
                batch_filename=batch_file.name
            )
            
            category_path = " > ".join(product_category)
            
            print(f"{i}. {title}")
            print(f"   价格: {price}")
            print(f"   图片数量: {image_count}")
            print(f"   分类: {category_path}")
            print(f"   来源: {product.get('source_url', '')[:80]}...")
            print()
            
        return 0, 0
    
    # 真实导入
    imported_count = 0
    error_count = 0
    
    for product in tqdm(products, desc="导入商品"):
        try:
            with transaction.atomic():
                # 确定分类
                batch_category = get_category_from_file(batch_file)
                category_path = determine_category(
                    product['title'], 
                    category_name=category_name, 
                    batch_filename=batch_file.name
                )
                
                # 获取或创建分类
                top_category = None
                second_category = None
                third_category = None
                
                # 获取顶级分类
                if len(category_path) > 0:
                    top_category, _ = GoodsCategory.objects.get_or_create(
                        name=category_path[0],
                        defaults={
                            'level': 1,
                            'description': f'{category_path[0]} category'
                        }
                    )
                
                # 获取二级分类
                if len(category_path) > 1 and top_category:
                    second_category, _ = GoodsCategory.objects.get_or_create(
                        name=category_path[1],
                        defaults={
                            'level': 2,
                            'parent': top_category,
                            'description': f'{category_path[1]} subcategory'
                        }
                    )
                
                # 获取三级分类
                if len(category_path) > 2 and second_category:
                    third_category, _ = GoodsCategory.objects.get_or_create(
                        name=category_path[2],
                        defaults={
                            'level': 3,
                            'parent': second_category,
                            'description': f'{category_path[2]} subcategory'
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
                            print(f"图片不存在: {image_path}")
                            continue
                        
                        # 创建商品图片
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

def extract_short_description(description):
    """
    从描述中提取简短描述
    """
    if not description:
        return "High-quality imported products."
    
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

def list_categories():
    """
    列出所有可用的分类和对应的系统分类
    """
    print("\n=== 可用分类映射 ===")
    print("亚马逊分类 => 系统分类路径")
    print("-" * 50)
    
    for amazon_category, system_path in sorted(CATEGORY_MAPPING.items()):
        system_category = " > ".join(system_path)
        print(f"{amazon_category} => {system_category}")

def main():
    parser = argparse.ArgumentParser(description='智能导入亚马逊商品数据')
    
    # 添加命令行参数
    parser.add_argument('--preview', action='store_true', help='只预览不实际导入')
    parser.add_argument('--batch', type=int, help='指定要导入的批次号')
    parser.add_argument('--category', type=str, help='指定商品分类')
    parser.add_argument('--list-categories', action='store_true', help='列出所有可用的分类映射')
    parser.add_argument('--limit', type=int, help='限制每个批次导入的商品数量')
    parser.add_argument('--directory', type=str, help='指定数据文件目录')
    
    args = parser.parse_args()
    
    if args.list_categories:
        list_categories()
        return
    
    # 获取批次文件
    batch_files = get_batch_files(args.directory, args.batch)
    
    if not batch_files:
        print("未找到匹配的批次文件")
        return
    
    print(f"找到 {len(batch_files)} 个批次文件")
    
    # 统计总数
    total_imported = 0
    total_errors = 0
    
    for batch_file in batch_files:
        imported, errors = import_batch(
            batch_file, 
            preview=args.preview, 
            category_name=args.category,
            limit=args.limit
        )
        
        if not args.preview:
            total_imported += imported
            total_errors += errors
    
    if not args.preview:
        print(f"\n导入完成: 共导入 {total_imported} 个商品, {total_errors} 个错误")
    else:
        print("\n这只是预览模式，没有实际导入数据")
        print("使用 --preview 参数来跳过预览并执行实际导入")

if __name__ == '__main__':
    main() 