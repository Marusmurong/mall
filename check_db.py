import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from django.db import connection

# 查询 wishlist_wishlistitem 表结构
with connection.cursor() as cursor:
    cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'wishlist_wishlistitem'
    ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    print("WishlistItem 表结构:")
    for col in columns:
        print(f"- {col[0]}: {col[1]}")

# 检查 purchased_by_id 是否存在
with connection.cursor() as cursor:
    cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'wishlist_wishlistitem' AND column_name = 'purchased_by_id';
    """)
    purchased_by_exists = cursor.fetchone()
    print(f"\npurchased_by_id 字段: {'存在' if purchased_by_exists else '不存在'}")

print("\n模型定义中的字段:")
from wishlist.models import WishlistItem
for field in WishlistItem._meta.fields:
    print(f"- {field.name}: {field.get_internal_type()}") 