import os
import django
from django.db import transaction

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入模型
from goods.models import GoodsCategory

# 定义分类结构
# 格式: 顶级分类 -> 二级分类 -> 三级分类
CATEGORY_STRUCTURE = {
    # 家居生活
    "Home Life": {
        "description": "Home & lifestyle products",
        "subcategories": {
            "Kitchen": {
                "description": "Kitchen appliances and accessories",
                "subcategories": {
                    "Cookware": {"description": "Pots, pans, and cooking utensils"},
                    "Bakeware": {"description": "Baking dishes, sheets, and tools"},
                    "Kitchen Tools": {"description": "Gadgets and tools for food preparation"}
                }
            },
            "Mugs & Cups": {
                "description": "Various mugs and cups for beverages",
                "subcategories": {
                    "Coffee Mugs": {"description": "Mugs designed for coffee"},
                    "Tea Cups": {"description": "Cups designed for tea"},
                    "Travel Mugs": {"description": "Portable mugs for on-the-go"}
                }
            },
            "Bathroom": {
                "description": "Bathroom accessories and decor",
                "subcategories": {
                    "Towels": {"description": "Bath and hand towels"},
                    "Bath Accessories": {"description": "Soap dishes, dispensers, and more"}
                }
            },
            "Bedding": {
                "description": "Sheets, blankets, and other bed items",
                "subcategories": {
                    "Sheets": {"description": "Bed sheets and pillowcases"},
                    "Comforters": {"description": "Comforters and duvets"},
                    "Pillows": {"description": "Pillows for sleeping"}
                }
            }
        }
    },
    
    # 电子产品
    "Electronics": {
        "description": "Electronic devices and accessories",
        "subcategories": {
            "Audio": {
                "description": "Audio equipment and accessories",
                "subcategories": {
                    "Headphones": {"description": "Over-ear, on-ear, and in-ear headphones"},
                    "Speakers": {"description": "Bluetooth, wired, and smart speakers"}
                }
            },
            "Mobile Accessories": {
                "description": "Accessories for smartphones and tablets",
                "subcategories": {
                    "Cases": {"description": "Protective cases for devices"},
                    "Chargers": {"description": "Wall, car, and wireless chargers"},
                    "Screen Protectors": {"description": "Tempered glass and film protectors"}
                }
            },
            "Computers": {
                "description": "Computer equipment and peripherals",
                "subcategories": {
                    "Laptops": {"description": "Portable computers"},
                    "Desktops": {"description": "Desktop computers"},
                    "Accessories": {"description": "Keyboard, mouse, and other accessories"}
                }
            }
        }
    },
    
    # 时尚服饰
    "Fashion": {
        "description": "Clothing, shoes, and accessories",
        "subcategories": {
            "Men's Clothing": {
                "description": "Clothing for men",
                "subcategories": {
                    "Shirts": {"description": "T-shirts, button-ups, and polos"},
                    "Pants": {"description": "Jeans, slacks, and shorts"},
                    "Outerwear": {"description": "Jackets, coats, and hoodies"}
                }
            },
            "Women's Clothing": {
                "description": "Clothing for women",
                "subcategories": {
                    "Tops": {"description": "Blouses, t-shirts, and sweaters"},
                    "Bottoms": {"description": "Pants, skirts, and shorts"},
                    "Dresses": {"description": "Casual and formal dresses"}
                }
            },
            "Accessories": {
                "description": "Fashion accessories",
                "subcategories": {
                    "Jewelry": {"description": "Necklaces, earrings, and bracelets"},
                    "Watches": {"description": "Wristwatches for men and women"},
                    "Bags": {"description": "Handbags, backpacks, and wallets"}
                }
            }
        }
    },
    
    # 礼品和装饰品
    "Gifts & Decor": {
        "description": "Gift items and home decorations",
        "subcategories": {
            "Personalized Gifts": {
                "description": "Customizable gift items",
                "subcategories": {
                    "Photo Gifts": {"description": "Customized photo frames and prints"},
                    "Engraved Items": {"description": "Engraved jewelry, pens, and more"},
                    "Custom Apparel": {"description": "Custom t-shirts and clothing"}
                }
            },
            "Home Decor": {
                "description": "Decorative items for the home",
                "subcategories": {
                    "Wall Art": {"description": "Wall hangings, paintings, and pictures"},
                    "Figurines": {"description": "Decorative figurines and sculptures"},
                    "Candles": {"description": "Scented and decorative candles"}
                }
            },
            "Seasonal Decor": {
                "description": "Holiday and seasonal decorations",
                "subcategories": {
                    "Christmas": {"description": "Christmas ornaments and decorations"},
                    "Halloween": {"description": "Halloween decor and props"},
                    "Spring & Easter": {"description": "Spring and Easter decorations"}
                }
            }
        }
    }
}

def create_category_structure():
    """
    根据定义的结构创建分类
    """
    # 使用事务确保数据一致性
    with transaction.atomic():
        # 清理现有分类
        should_clear = input("Do you want to clear existing categories? (yes/no): ").lower()
        if should_clear in ['yes', 'y']:
            GoodsCategory.objects.all().delete()
            print("Deleted all existing categories.")
            
        # 创建分类结构
        for top_name, top_data in CATEGORY_STRUCTURE.items():
            # 创建顶级分类
            top_category, created = GoodsCategory.objects.get_or_create(
                name=top_name,
                defaults={
                    'level': 1,
                    'description': top_data['description']
                }
            )
            status = "Created" if created else "Found existing"
            print(f"{status} top category: {top_name}")
            
            # 创建二级分类
            for second_name, second_data in top_data['subcategories'].items():
                second_category, created = GoodsCategory.objects.get_or_create(
                    name=second_name,
                    defaults={
                        'level': 2,
                        'parent': top_category,
                        'description': second_data['description']
                    }
                )
                status = "Created" if created else "Found existing"
                print(f"  {status} second-level category: {second_name}")
                
                # 创建三级分类
                if 'subcategories' in second_data:
                    for third_name, third_data in second_data['subcategories'].items():
                        third_category, created = GoodsCategory.objects.get_or_create(
                            name=third_name,
                            defaults={
                                'level': 3,
                                'parent': second_category,
                                'description': third_data['description']
                            }
                        )
                        status = "Created" if created else "Found existing"
                        print(f"    {status} third-level category: {third_name}")
    
    print("\nCategory structure creation completed.")
    print(f"Total categories: {GoodsCategory.objects.count()}")
    print(f"- Level 1: {GoodsCategory.objects.filter(level=1).count()}")
    print(f"- Level 2: {GoodsCategory.objects.filter(level=2).count()}")
    print(f"- Level 3: {GoodsCategory.objects.filter(level=3).count()}")

def check_existing_categories():
    """
    检查现有分类
    """
    print("\nExisting categories:")
    top_categories = GoodsCategory.objects.filter(level=1)
    
    for top in top_categories:
        print(f"- {top.name}")
        second_categories = GoodsCategory.objects.filter(parent=top)
        
        for second in second_categories:
            print(f"  - {second.name}")
            third_categories = GoodsCategory.objects.filter(parent=second)
            
            for third in third_categories:
                print(f"    - {third.name}")

def assign_existing_products():
    """
    为已有商品分配到正确的分类
    """
    from goods.models import Goods
    
    # 查找"Mugs & Cups"分类
    try:
        mugs_category = GoodsCategory.objects.get(name="Mugs & Cups")
        coffee_mugs_category = GoodsCategory.objects.filter(name="Coffee Mugs", parent=mugs_category).first()
        
        # 如果coffee_mugs_category不存在，使用mugs_category
        target_category = coffee_mugs_category if coffee_mugs_category else mugs_category
        
        # 计数器
        count = 0
        
        # 获取所有商品
        products = Goods.objects.all()
        
        for product in products:
            # 检查产品名称是否包含"Mug"或"Cup"
            if "mug" in product.name.lower() or "cup" in product.name.lower():
                product.category = target_category
                product.save()
                count += 1
                print(f"Assigned product to {target_category.name}: {product.name}")
        
        print(f"\nAssigned {count} products to {target_category.name} category")
    
    except GoodsCategory.DoesNotExist:
        print("Category 'Mugs & Cups' not found. Please create the category structure first.")

if __name__ == '__main__':
    print("Category Management Tool")
    print("------------------------")
    print("1. Create/Update Category Structure")
    print("2. Check Existing Categories")
    print("3. Assign Existing Mug Products to Correct Category")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        create_category_structure()
    elif choice == '2':
        check_existing_categories()
    elif choice == '3':
        assign_existing_products()
    else:
        print("Exiting program.") 