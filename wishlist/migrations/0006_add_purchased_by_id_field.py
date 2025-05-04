from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('wishlist', '0005_fix_current_payment_id_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistitem',
            name='purchased_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='purchased_items',
                to='auth.user',
                verbose_name='购买者',
            ),
        ),
    ] 