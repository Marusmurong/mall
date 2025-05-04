import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from goods.models import Goods, GoodsImage

class Command(BaseCommand):
    help = '删除处于草稿状态的商品及其关联的图片文件'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='仅显示要删除的内容，不实际删除',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='强制删除所有商品，忽略外键错误',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        # 获取所有草稿状态的商品
        draft_goods = Goods.objects.filter(status='draft')
        
        if not draft_goods.exists():
            self.stdout.write(self.style.SUCCESS('没有找到草稿状态的商品'))
            return
        
        self.stdout.write(f'找到 {draft_goods.count()} 个草稿状态的商品')
        
        total_goods_deleted = 0
        total_images_deleted = 0
        total_files_deleted = 0
        
        for goods in draft_goods:
            self.stdout.write(f'处理商品: {goods.name} (ID: {goods.id})')
            
            # 收集与商品关联的所有图片文件路径
            image_paths = []
            
            # 添加主图
            if goods.image:
                image_paths.append(goods.image.path)
            
            # 收集所有商品图片
            goods_images = GoodsImage.objects.filter(goods=goods)
            for image in goods_images:
                if image.image:
                    image_paths.append(image.image.path)
            
            if dry_run:
                self.stdout.write(f'  将删除商品: {goods.name}')
                for path in image_paths:
                    self.stdout.write(f'  将删除图片文件: {path}')
            else:
                # 删除物理文件
                for path in image_paths:
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                            self.stdout.write(self.style.SUCCESS(f'  已删除图片文件: {path}'))
                            total_files_deleted += 1
                        else:
                            self.stdout.write(self.style.WARNING(f'  文件不存在: {path}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  删除文件时出错: {path} - {e}'))
                
                # 删除数据库中的图片记录
                num_images = goods_images.count()
                goods_images.delete()
                total_images_deleted += num_images
                
                # 删除商品
                try:
                    with transaction.atomic():
                        goods_name = goods.name
                        goods.delete()
                        total_goods_deleted += 1
                        self.stdout.write(self.style.SUCCESS(f'  已删除商品: {goods_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  删除商品时出错: {goods.name} (ID: {goods.id}) - {e}'))
                    if force:
                        try:
                            # 如果启用了force选项，尝试绕过级联删除
                            self.stdout.write(self.style.WARNING(f'  尝试强制删除商品: {goods.name} (ID: {goods.id})'))
                            # 更新商品状态为'deleted'而不是实际删除
                            goods.status = 'deleted'
                            goods.save()
                            self.stdout.write(self.style.SUCCESS(f'  已将商品状态设置为deleted: {goods.name}'))
                            total_goods_deleted += 1
                        except Exception as e2:
                            self.stdout.write(self.style.ERROR(f'  强制删除商品时出错: {goods.name} (ID: {goods.id}) - {e2}'))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'[模拟运行] 总共将删除 {draft_goods.count()} 个商品和相关的图片文件'))
        else:
            self.stdout.write(self.style.SUCCESS(f'总共删除了 {total_goods_deleted} 个商品, {total_images_deleted} 条图片记录, {total_files_deleted} 个图片文件'))

        # 检查孤立的图片文件夹
        if not dry_run:
            self.clean_empty_directories(os.path.join(settings.MEDIA_ROOT, 'goods/images/'))
    
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