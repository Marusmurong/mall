import json
import os
import re
from django.core.management.base import BaseCommand
from goods.models import Goods, GoodsImage, GoodsCategory
from django.db import transaction

class Command(BaseCommand):
    help = '从指定 JSON 文件导入商品，按分类名称或ID自动关联，图片插入到详情和图片库，商品状态为发布。支持 --limit/--offset 参数控制导入范围。'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='商品 JSON 文件路径')
        parser.add_argument('--limit', type=int, default=None, help='只导入前N个商品')
        parser.add_argument('--offset', type=int, default=0, help='跳过前M个商品')

    def to_local_image_path(self, img_url):
        filename = os.path.basename(img_url)
        return f'goods/images/{filename}'  # 只保留相对路径，不加/media/

    def handle(self, *args, **options):
        json_file = options['json_file']
        limit = options['limit']
        offset = options['offset']
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'文件不存在: {json_file}'))
            return
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read().lstrip()
            if content.startswith('['):
                data = json.loads(content)
            else:
                lines = content.splitlines()
                json_str = ''.join(lines[2:])
                data = json.loads(json_str)
        categories = GoodsCategory.objects.all()
        cat_id_map = {c.pk: c for c in categories}
        cat_name_map = {c.name.strip().lower(): c for c in categories}
        goods_items = [item for item in data if item.get('model') == 'goods.goods']
        if offset:
            goods_items = goods_items[offset:]
        if limit:
            goods_items = goods_items[:limit]
        self.stdout.write(self.style.SUCCESS(f'准备导入 {len(goods_items)} 个商品'))
        imported = 0
        with transaction.atomic():
            for item in goods_items:
                pk = item.get('pk')
                fields = item.get('fields', {})
                name = fields.get('name')
                category_id = fields.get('category')
                category_name = fields.get('category_name', None)
                category = cat_id_map.get(category_id)
                if not category and category_name:
                    category = cat_name_map.get(category_name.strip().lower())
                if not category:
                    self.stdout.write(self.style.WARNING(f'分类未找到: id={category_id}, name={category_name}，商品 {name} 跳过'))
                    continue
                price = fields.get('price', 0)
                original_price = fields.get('original_price', 0)
                stock = fields.get('stock', 0)
                image_url = fields.get('image', None)
                description = fields.get('description', '')
                goods_desc = fields.get('goods_desc', '')
                images = fields.get('images', [])
                # 构建所有图片本地路径列表，去重
                all_images = []
                if image_url:
                    local_img = self.to_local_image_path(image_url)
                    all_images.append(local_img)
                if isinstance(images, list):
                    for img in images:
                        if img:
                            local_img = self.to_local_image_path(img)
                            if local_img not in all_images:
                                all_images.append(local_img)
                # 详情内容只留一份，优先 goods_desc
                if goods_desc:
                    desc_with_imgs = goods_desc.strip()
                elif description:
                    desc_with_imgs = description.strip()
                else:
                    desc_with_imgs = ''
                    for img_url in all_images:
                        desc_with_imgs += f'<br><img src="{img_url}" style="max-width:100%">'
                # description 字段统一置空
                good, created = Goods.objects.update_or_create(
                    pk=pk,
                    defaults={
                        'name': name,
                        'category': category,
                        'price': price,
                        'original_price': original_price,
                        'stock': stock,
                        'description': '',  # 只保留 goods_desc
                        'goods_desc': desc_with_imgs,
                        'status': 'published',
                        'image': all_images[0] if all_images else None,
                        'is_recommended': fields.get('is_recommended', False),
                        'is_hot': fields.get('is_hot', False),
                        'is_new': fields.get('is_new', True),
                        'source_url': fields.get('source_url', ''),
                        'visible_in': [],
                    }
                )
                # 商品图片库写入所有图片
                GoodsImage.objects.filter(goods=good).delete()
                for idx, img_url in enumerate(all_images):
                    GoodsImage.objects.create(
                        goods=good,
                        image=img_url,
                        is_main=(idx == 0),
                        sort_order=idx
                    )
                imported += 1
                self.stdout.write(self.style.SUCCESS(f'已导入商品: {name}'))
        self.stdout.write(self.style.SUCCESS(f'全部导入完成，共导入 {imported} 个商品'))
