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

# 检查admin配置
from django.contrib import admin
from goods.models import Goods, GoodsCategory
from django.apps import apps

def main():
    """检查admin配置"""
    # 检查模型是否已注册到admin
    print("检查模型是否已注册到admin:")
    all_models = apps.get_models()
    
    print(f"所有已注册的模型:")
    for model, admin_instance in admin.site._registry.items():
        print(f"- {model.__name__} 已注册，管理类为 {admin_instance.__class__.__name__}")
    
    # 特别检查Goods和GoodsCategory
    goods_registered = Goods in [model for model, _ in admin.site._registry.items()]
    category_registered = GoodsCategory in [model for model, _ in admin.site._registry.items()]
    
    print(f"\nGoods模型是否已注册到admin: {goods_registered}")
    print(f"GoodsCategory模型是否已注册到admin: {category_registered}")
    
    # 检查admin对应的文件
    print("\n检查admin.py文件:")
    try:
        from goods import admin as goods_admin
        print("goods.admin已成功导入")
        
        # 打印goods.admin模块中的所有内容
        print("goods.admin模块中的内容:")
        for item_name in dir(goods_admin):
            if not item_name.startswith('__'):
                item = getattr(goods_admin, item_name)
                print(f"- {item_name}: {type(item)}")
    except ImportError as e:
        print(f"导入goods.admin失败: {e}")
    
    # 尝试访问几个商品实例
    print("\n尝试访问商品实例:")
    try:
        goods_count = Goods.objects.count()
        print(f"商品总数: {goods_count}")
        
        if goods_count > 0:
            print("前5个商品:")
            for g in Goods.objects.all()[:5]:
                print(f"- ID: {g.id}, 名称: {g.name}, 分类: {g.category.name if g.category else 'None'}")
    except Exception as e:
        print(f"访问商品失败: {e}")

if __name__ == "__main__":
    main() 