# Generated by Django 5.1.7 on 2025-03-30 03:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='external_order_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='外部订单号'),
        ),
        migrations.AddField(
            model_name='order',
            name='is_anonymous_payer',
            field=models.BooleanField(default=False, verbose_name='匿名付款'),
        ),
        migrations.AddField(
            model_name='order',
            name='payer_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='付款人邮箱'),
        ),
        migrations.AddField(
            model_name='order',
            name='payer_message',
            field=models.TextField(blank=True, null=True, verbose_name='付款人留言'),
        ),
        migrations.AddField(
            model_name='order',
            name='payer_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='付款人姓名'),
        ),
        migrations.AddField(
            model_name='order',
            name='payer_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='付款人电话'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_account',
            field=models.CharField(blank=True, max_length=100, verbose_name='支付账号'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50, verbose_name='支付方式'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_notes',
            field=models.TextField(blank=True, verbose_name='支付备注'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_platform',
            field=models.CharField(blank=True, max_length=50, verbose_name='支付平台'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_proof',
            field=models.ImageField(blank=True, null=True, upload_to='payment_proofs/', verbose_name='支付凭证'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(blank=True, max_length=30, verbose_name='支付状态'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='支付时间'),
        ),
        migrations.AddField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='交易号/流水号'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='心愿单所有者'),
        ),
    ]
