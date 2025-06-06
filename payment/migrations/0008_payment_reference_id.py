# Generated by Django 5.1.7 on 2025-04-30 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_alter_payment_wishlist_item_id_to_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='reference_id',
            field=models.CharField(blank=True, help_text='Unique reference for payment', max_length=64, null=True, unique=True),
        ),
    ]
