from django.core.management.base import BaseCommand
from goods.models import Goods, GoodsImage

class Command(BaseCommand):
    help = '删除空的商品数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将被删除的商品，不实际删除',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        # 查找空商品（名称为空或价格为0的商品）
        empty_goods = Goods.objects.filter(name='-') | Goods.objects.filter(price=0.0)
        
        # 计数
        count = empty_goods.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('没有找到空商品数据'))
            return
        
        self.stdout.write(f'找到 {count} 个空商品数据')
        
        # 显示前10个将被删除的商品
        for i, good in enumerate(empty_goods[:10]):
            self.stdout.write(f'{i+1}. ID: {good.id}, 名称: {good.name}, 价格: {good.price}, 分类: {good.category.name}')
        
        if count > 10:
            self.stdout.write(f'... 以及 {count - 10} 个其他商品')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('这是一个预演，没有删除任何数据'))
            self.stdout.write(self.style.WARNING('使用 python manage.py delete_empty_goods 命令来实际删除这些数据'))
            return
        
        # 删除相关的商品图片
        image_count = 0
        for good in empty_goods:
            image_count += good.images.count()
            
        self.stdout.write(f'将删除 {image_count} 个相关的商品图片')
        
        # 执行删除
        if not dry_run:
            # 先删除图片
            for good in empty_goods:
                good.images.all().delete()
            
            # 再删除商品
            empty_goods.delete()
            
            self.stdout.write(self.style.SUCCESS(f'成功删除 {count} 个空商品数据和 {image_count} 个相关的商品图片'))
