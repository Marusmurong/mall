import os
from django.core.management.base import BaseCommand
from django.conf import settings
from goods.models import Goods, GoodsImage

class Command(BaseCommand):
    help = '清理孤立的商品图片文件（存在于文件系统但在数据库中没有引用的图片）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='仅显示要删除的内容，不实际删除',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 获取所有数据库中引用的图片路径
        db_image_paths = set()
        
        # 收集商品主图
        for goods in Goods.objects.all():
            if goods.image:
                db_image_paths.add(os.path.abspath(goods.image.path))
        
        # 收集商品图片
        for image in GoodsImage.objects.all():
            if image.image:
                db_image_paths.add(os.path.abspath(image.image.path))
        
        self.stdout.write(f'数据库中引用了 {len(db_image_paths)} 个商品图片')
        
        # 扫描文件系统中的图片
        images_dir = os.path.join(settings.MEDIA_ROOT, 'goods/images/')
        if not os.path.exists(images_dir):
            self.stdout.write(self.style.WARNING(f'商品图片目录不存在: {images_dir}'))
            return
        
        orphaned_images = []
        
        for root, dirs, files in os.walk(images_dir):
            for file in files:
                if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    full_path = os.path.abspath(os.path.join(root, file))
                    if full_path not in db_image_paths:
                        orphaned_images.append(full_path)
        
        self.stdout.write(f'找到 {len(orphaned_images)} 个孤立的图片文件')
        
        if dry_run:
            for path in orphaned_images:
                self.stdout.write(f'  将删除孤立图片: {path}')
            self.stdout.write(self.style.SUCCESS(f'[模拟运行] 总共将删除 {len(orphaned_images)} 个孤立图片文件'))
        else:
            deleted_count = 0
            for path in orphaned_images:
                try:
                    os.remove(path)
                    self.stdout.write(self.style.SUCCESS(f'  已删除孤立图片: {path}'))
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  删除孤立图片时出错: {path} - {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'总共删除了 {deleted_count} 个孤立图片文件'))
            
            # 清理空目录
            self.clean_empty_directories(images_dir)
    
    def clean_empty_directories(self, start_dir):
        """递归删除空目录"""
        empty_dirs_removed = 0
        
        for root, dirs, files in os.walk(start_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                
                # 检查目录是否为空
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                        self.stdout.write(self.style.SUCCESS(f'已删除空目录: {dir_path}'))
                        empty_dirs_removed += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'删除目录时出错: {dir_path} - {e}'))
        
        if empty_dirs_removed > 0:
            self.stdout.write(self.style.SUCCESS(f'总共删除了 {empty_dirs_removed} 个空目录')) 