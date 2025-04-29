#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入模型
from goods.models import Goods

def check_products():
    # 获取总商品数
    total_count = Goods.objects.count()
    print(f"总商品数: {total_count}")
    
    # 获取最新导入的商品
    latest_products = Goods.objects.order_by('-created_at')[:5]
    
    print("\n最新导入的商品:")
    for idx, product in enumerate(latest_products, 1):
        category_path = []
        category = product.category
        
        # 构建分类路径
        while category:
            category_path.insert(0, category.name)
            category = category.parent
            
        category_str = " > ".join(category_path)
        
        # 显示商品信息
        title = product.title if hasattr(product, 'title') else product.name
        title_preview = title[:50] + "..." if len(title) > 50 else title
        
        print(f"{idx}. {title_preview}")
        print(f"   价格: ${product.price}")
        print(f"   分类: {category_str}")
        print(f"   创建时间: {product.created_at}")
        print()

if __name__ == "__main__":
    check_products() 