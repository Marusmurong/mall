#!/usr/bin/env python
"""
Script to delete excess goods from the database, keeping only the first 20 items.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from goods.models import Goods, GoodsImage

# Count total goods
total_goods = Goods.objects.count()
print(f"Total goods before deletion: {total_goods}")

# Get all goods IDs
all_goods_ids = list(Goods.objects.values_list('id', flat=True).order_by('id'))

# Keep only the first 20 goods
goods_to_keep = all_goods_ids[:20]
goods_to_delete = all_goods_ids[20:]

# Print information about what will be deleted
print(f"Keeping {len(goods_to_keep)} goods with IDs: {goods_to_keep}")
print(f"Deleting {len(goods_to_delete)} goods")

# Delete the excess goods
delete_count, _ = Goods.objects.filter(id__in=goods_to_delete).delete()

# Count remaining goods
remaining_goods = Goods.objects.count()
print(f"Deleted {delete_count} goods")
print(f"Total goods after deletion: {remaining_goods}")
print("Operation completed successfully.")
