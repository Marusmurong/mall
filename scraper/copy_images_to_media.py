#!/usr/bin/env python
"""
将scraped_images目录下的图片复制到media目录，保持相同的子目录结构
"""
import os
import sys
import shutil
import django
from pathlib import Path

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from goods.models import Goods, GoodsImage

# 定义源目录和目标目录
SOURCE_DIR = BASE_DIR / "scraped_images"
MEDIA_DIR = BASE_DIR / "media"

def ensure_directory(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")

def copy_goods_images():
    """根据数据库中的图片记录，复制图片到media目录"""
    print("开始复制商品图片...")
    
    # 获取所有商品图片
    images = GoodsImage.objects.all()
    total = images.count()
    print(f"找到 {total} 条图片记录")
    
    copied = 0
    skipped = 0
    
    for img in images:
        if not img.image:
            skipped += 1
            continue
        
        rel_path = str(img.image)
        # 构建源文件和目标文件路径
        source_file = SOURCE_DIR / rel_path
        target_dir = MEDIA_DIR / os.path.dirname(rel_path)
        target_file = MEDIA_DIR / rel_path
        
        # 确保目标目录存在
        ensure_directory(target_dir)
        
        # 如果源文件存在且目标文件不存在或源文件更新，则复制
        if os.path.exists(source_file) and (not os.path.exists(target_file) or 
                                           os.path.getmtime(source_file) > os.path.getmtime(target_file)):
            try:
                shutil.copy2(source_file, target_file)
                copied += 1
                print(f"复制图片: {source_file} -> {target_file}")
            except Exception as e:
                print(f"复制失败: {rel_path}, 错误: {e}")
                skipped += 1
        else:
            if not os.path.exists(source_file):
                print(f"源文件不存在: {source_file}")
            skipped += 1
    
    print(f"商品图片复制完成: 成功 {copied}, 跳过 {skipped}")
    return copied, skipped

def copy_goods_main_images():
    """复制商品主图"""
    print("\n开始复制商品主图...")
    
    # 获取所有商品
    goods_list = Goods.objects.exclude(image='')
    total = goods_list.count()
    print(f"找到 {total} 条商品主图记录")
    
    copied = 0
    skipped = 0
    
    for goods in goods_list:
        if not goods.image:
            skipped += 1
            continue
        
        rel_path = str(goods.image)
        # 构建源文件和目标文件路径
        source_file = SOURCE_DIR / rel_path
        target_dir = MEDIA_DIR / os.path.dirname(rel_path)
        target_file = MEDIA_DIR / rel_path
        
        # 确保目标目录存在
        ensure_directory(target_dir)
        
        # 如果源文件存在且目标文件不存在或源文件更新，则复制
        if os.path.exists(source_file) and (not os.path.exists(target_file) or 
                                           os.path.getmtime(source_file) > os.path.getmtime(target_file)):
            try:
                shutil.copy2(source_file, target_file)
                copied += 1
                print(f"复制主图: {source_file} -> {target_file}")
            except Exception as e:
                print(f"复制失败: {rel_path}, 错误: {e}")
                skipped += 1
        else:
            if not os.path.exists(source_file):
                print(f"源文件不存在: {source_file}")
            skipped += 1
    
    print(f"商品主图复制完成: 成功 {copied}, 跳过 {skipped}")
    return copied, skipped

if __name__ == "__main__":
    print("=== 开始将图片从scraped_images复制到media目录 ===")
    
    # 确保目标根目录存在
    ensure_directory(MEDIA_DIR)
    
    # 复制商品图片
    img_copied, img_skipped = copy_goods_images()
    
    # 复制商品主图
    main_copied, main_skipped = copy_goods_main_images()
    
    print("\n=== 复制完成 ===")
    print(f"总计: 复制 {img_copied + main_copied} 张图片, 跳过 {img_skipped + main_skipped} 张图片") 