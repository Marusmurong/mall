from django.core.management.base import BaseCommand
from django.db.models import Count
from goods.models import GoodsCategory

class Command(BaseCommand):
    help = '删除没有关联商品的3级分类'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='仅显示要删除的内容，不实际删除',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 查找所有3级分类
        level3_categories = GoodsCategory.objects.filter(level=3)
        
        if not level3_categories.exists():
            self.stdout.write(self.style.SUCCESS('没有找到3级分类'))
            return
        
        self.stdout.write(f'找到 {level3_categories.count()} 个3级分类')
        
        # 查找没有商品的3级分类
        empty_categories = level3_categories.annotate(goods_count=Count('goods')).filter(goods_count=0)
        
        if not empty_categories.exists():
            self.stdout.write(self.style.SUCCESS('没有找到空的3级分类'))
            return
        
        # 预先收集分类信息，避免删除后无法访问父分类信息
        categories_to_delete = []
        for category in empty_categories:
            try:
                parent_name = "无父级分类"
                if category.parent_id:
                    try:
                        parent = GoodsCategory.objects.get(id=category.parent_id)
                        parent_name = parent.name
                    except GoodsCategory.DoesNotExist:
                        parent_name = f"未知(ID:{category.parent_id})"
                
                categories_to_delete.append({
                    'id': category.id,
                    'name': category.name,
                    'parent_name': parent_name,
                    'instance': category
                })
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理分类信息时出错: {category.id} - {e}'))
        
        self.stdout.write(f'找到 {len(categories_to_delete)} 个没有商品的3级分类')
        
        # 删除分类
        deleted_count = 0
        for category_info in categories_to_delete:
            if dry_run:
                self.stdout.write(f'将删除分类: {category_info["name"]} (ID: {category_info["id"]}, 父分类: {category_info["parent_name"]})')
            else:
                try:
                    category_info['instance'].delete()
                    self.stdout.write(self.style.SUCCESS(
                        f'已删除分类: {category_info["name"]} (ID: {category_info["id"]}, 父分类: {category_info["parent_name"]}'))
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'删除分类时出错: {category_info["name"]} (ID: {category_info["id"]}) - {e}'))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'[模拟运行] 总共将删除 {len(categories_to_delete)} 个空的3级分类'))
        else:
            self.stdout.write(self.style.SUCCESS(f'总共删除了 {deleted_count} 个空的3级分类')) 