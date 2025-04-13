#!/usr/bin/env python
import os
import sys
import shutil
from pathlib import Path
import django

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from django.conf import settings
from goods.models import GoodsImage, Goods

def main():
    """
    Copy images from scraped_images directory to media directory and update database references.
    """
    # Ensure media directory exists
    media_dir = settings.MEDIA_ROOT
    scraped_dir = os.path.join(settings.BASE_DIR, 'scraped_images')
    
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    # Check for drharness_new directory
    source_dir = os.path.join(scraped_dir, 'drharness_new')
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} does not exist!")
        return
    
    # Create target directory
    target_dir = os.path.join(media_dir, 'drharness_new')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Copy all product directories
    products_copied = 0
    images_copied = 0
    
    for product_dir in os.listdir(source_dir):
        # Skip hidden files like .DS_Store
        if product_dir.startswith('.'):
            continue
        
        source_product_path = os.path.join(source_dir, product_dir)
        target_product_path = os.path.join(target_dir, product_dir)
        
        # Skip if not a directory
        if not os.path.isdir(source_product_path):
            continue
        
        # Create product directory in media
        if os.path.exists(target_product_path):
            # Remove existing directory to ensure clean copy
            shutil.rmtree(target_product_path)
        
        # Create new directory
        os.makedirs(target_product_path)
        
        # Copy all images
        for image_file in os.listdir(source_product_path):
            source_image_path = os.path.join(source_product_path, image_file)
            target_image_path = os.path.join(target_product_path, image_file)
            
            if os.path.isfile(source_image_path):
                shutil.copy2(source_image_path, target_image_path)
                images_copied += 1
        
        products_copied += 1
        print(f"Copied directory: {product_dir} with its images")
    
    print(f"Copied {images_copied} images for {products_copied} products")
    
    # Update database references
    goods_updated = 0
    images_updated = 0
    
    # Update Goods model image field
    for goods in Goods.objects.all():
        if goods.image and 'scraped_images/' in goods.image:
            goods.image = goods.image.replace('scraped_images/', '')
            goods.save(update_fields=['image'])
            goods_updated += 1
    
    # Update GoodsImage model image field
    for image in GoodsImage.objects.all():
        if 'scraped_images/' in image.image:
            image.image = image.image.replace('scraped_images/', '')
            image.save(update_fields=['image'])
            images_updated += 1
    
    print(f"Updated {goods_updated} goods and {images_updated} image records in database")
    print("All operations complete! Product images should now display correctly.")

if __name__ == "__main__":
    main() 