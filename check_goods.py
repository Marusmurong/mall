#!/usr/bin/env python
import os
import django
import sys
from pathlib import Path

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入模型
from goods.models import Goods, GoodsCategory

def main():
    """检查商品数据"""
    # 打印总体统计
    print(f"总商品数: {Goods.objects.count()}")
    print(f"DrHarness商品数: {Goods.objects.filter(source_url__contains='drharness').count()}")
    
    # 打印各分类的商品数
    print("\n商品分类统计:")
    for cat in GoodsCategory.objects.all():
        goods_count = Goods.objects.filter(category=cat).count()
        print(f"{cat.id}: {cat.name} - 商品数: {goods_count}")
    
    # 打印没有图片的商品
    print("\n没有主图的商品:")
    for g in Goods.objects.filter(image=''):
        print(f"{g.id}: {g.name}")
    
    # 列出几个最近添加的商品
    print("\n最近添加的商品:")
    for g in Goods.objects.all().order_by('-id')[:10]:
        print(f"{g.id}: {g.name} (分类: {g.category.name}, 来源: {g.source_url})")

if __name__ == "__main__":
    main() 