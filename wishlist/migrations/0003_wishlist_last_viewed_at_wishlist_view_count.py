# Generated by Django 5.1.7 on 2025-04-13 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0002_alter_wishlistitem_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='last_viewed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='最后访问时间'),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='view_count',
            field=models.PositiveIntegerField(default=0, verbose_name='访问量'),
        ),
    ]
