# Generated by Django 5.1.7 on 2025-03-30 04:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='goods_desc',
            field=models.TextField(blank=True, verbose_name='商品详细描述'),
        ),
        migrations.AddField(
            model_name='goods',
            name='source_url',
            field=models.URLField(blank=True, max_length=500, verbose_name='商品来源URL'),
        ),
        migrations.AddField(
            model_name='goodscategory',
            name='description',
            field=models.TextField(blank=True, verbose_name='分类描述'),
        ),
        migrations.CreateModel(
            name='GoodsImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='goods/images/', verbose_name='图片')),
                ('is_main', models.BooleanField(default=False, verbose_name='是否主图')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='排序')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='goods.goods', verbose_name='商品')),
            ],
            options={
                'verbose_name': '商品图片',
                'verbose_name_plural': '商品图片',
                'ordering': ['sort_order', 'created_at'],
            },
        ),
    ]
