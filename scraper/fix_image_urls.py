#!/usr/bin/env python
"""
修复图片URL脚本：将Goods和GoodsImage表中保存的完整URL替换为正确的相对路径
"""
import os
import sys
import django
from pathlib import Path
from urllib.parse import unquote, urlparse

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from goods.models import Goods, GoodsImage

def fix_goods_images():
    """修复GoodsImage表中的图片URL"""
    print("开始修复GoodsImage表中的图片URL...")
    
    # 查找使用http/https开头的图片URL
    images = GoodsImage.objects.filter(image__startswith='http')
    count = images.count()
    print(f"找到{count}个需要修复的图片记录")
    
    fixed = 0
    for img in images:
        # 获取原始URL
        old_url = str(img.image)
        print(f"原始URL: {old_url}")
        
        # 解析URL
        parsed_url = urlparse(old_url)
        # 提取文件名
        filename = Path(parsed_url.path).name
        # 清理查询参数（如果有）
        if '?' in filename:
            filename = filename.split('?')[0]
        
        # 从商品名称创建目录名
        product_dir = img.goods.name.lower().replace(' ', '-')
        # 构建新的相对路径
        new_path = f"{product_dir}/{filename}"
        
        # 检查本地文件是否存在
        local_file_path = os.path.join(BASE_DIR, "scraped_images", product_dir, filename)
        if os.path.exists(local_file_path):
            # 更新数据库记录
            img.image = new_path
            img.save()
            fixed += 1
            print(f"已修复: {old_url} -> {new_path}")
        else:
            print(f"警告: 本地文件不存在: {local_file_path}")
    
    print(f"完成GoodsImage表修复，成功修复{fixed}/{count}个记录")
    return fixed

def fix_goods_main_images():
    """修复Goods表中的主图URL"""
    print("\n开始修复Goods表中的主图URL...")
    
    # 查找使用http/https开头的主图URL
    goods_list = Goods.objects.filter(image__startswith='http')
    count = goods_list.count()
    print(f"找到{count}个需要修复的商品主图记录")
    
    fixed = 0
    for goods in goods_list:
        # 获取原始URL
        old_url = str(goods.image)
        print(f"原始URL: {old_url}")
        
        # 解析URL
        parsed_url = urlparse(old_url)
        # 提取文件名
        filename = Path(parsed_url.path).name
        # 清理查询参数（如果有）
        if '?' in filename:
            filename = filename.split('?')[0]
        
        # 从商品名称创建目录名
        product_dir = goods.name.lower().replace(' ', '-')
        # 构建新的相对路径
        new_path = f"{product_dir}/{filename}"
        
        # 检查本地文件是否存在
        local_file_path = os.path.join(BASE_DIR, "scraped_images", product_dir, filename)
        if os.path.exists(local_file_path):
            # 更新数据库记录
            goods.image = new_path
            goods.save(update_fields=['image'])
            fixed += 1
            print(f"已修复: {old_url} -> {new_path}")
        else:
            # 尝试使用商品的第一张图片作为主图
            main_image = goods.images.filter(is_main=True).first() or goods.images.first()
            if main_image and not str(main_image.image).startswith('http'):
                goods.image = main_image.image
                goods.save(update_fields=['image'])
                fixed += 1
                print(f"已修复(使用现有图片): {old_url} -> {main_image.image}")
            else:
                print(f"警告: 找不到可替换的图片: {goods.name}")
    
    print(f"完成Goods表修复，成功修复{fixed}/{count}个记录")
    return fixed

if __name__ == "__main__":
    print("=== 开始修复图片URL ===")
    image_fixed = fix_goods_images()
    goods_fixed = fix_goods_main_images()
    print("\n=== 修复完成 ===")
    print(f"总计修复 {image_fixed} 个商品图片记录和 {goods_fixed} 个商品主图记录") 