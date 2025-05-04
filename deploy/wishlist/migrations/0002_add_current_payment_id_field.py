from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0001_initial'),  # 请确保依赖于前一个迁移
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistitem',
            name='current_payment_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='当前支付ID'),
        ),
    ] 