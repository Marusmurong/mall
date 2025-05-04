from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from goods.models import GoodsCategory

class Command(BaseCommand):
    help = '删除没有关联商品且没有二级子分类的一级分类'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='仅显示要删除的内容，不实际删除',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 查找所有1级分类
        level1_categories = GoodsCategory.objects.filter(level=1)
        
        if not level1_categories.exists():
            self.stdout.write(self.style.SUCCESS('没有找到1级分类'))
            return
        
        self.stdout.write(f'找到 {level1_categories.count()} 个1级分类')
        
        # 查找没有商品且没有子分类的1级分类
        empty_categories = level1_categories.annotate(
            goods_count=Count('goods'),
            children_count=Count('children')
        ).filter(goods_count=0, children_count=0)
        
        if not empty_categories.exists():
            self.stdout.write(self.style.SUCCESS('没有找到符合条件的1级分类'))
            return
        
        # 预先收集分类信息
        categories_to_delete = []
        for category in empty_categories:
            try:
                categories_to_delete.append({
                    'id': category.id,
                    'name': category.name,
                    'instance': category
                })
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理分类信息时出错: {category.id} - {e}'))
        
        self.stdout.write(f'找到 {len(categories_to_delete)} 个没有商品且没有二级子分类的1级分类')
        
        # 删除分类
        deleted_count = 0
        for category_info in categories_to_delete:
            if dry_run:
                self.stdout.write(f'将删除分类: {category_info["name"]} (ID: {category_info["id"]})')
            else:
                try:
                    category_info['instance'].delete()
                    self.stdout.write(self.style.SUCCESS(
                        f'已删除分类: {category_info["name"]} (ID: {category_info["id"]})'))
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'删除分类时出错: {category_info["name"]} (ID: {category_info["id"]}) - {e}'))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'[模拟运行] 总共将删除 {len(categories_to_delete)} 个空的1级分类'))
        else:
            self.stdout.write(self.style.SUCCESS(f'总共删除了 {deleted_count} 个空的1级分类')) 