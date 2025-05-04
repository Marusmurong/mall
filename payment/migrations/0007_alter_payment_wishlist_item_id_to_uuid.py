from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_alter_payment_wishlist_item_to_uuid'),
    ]

    operations = [
        # 1. 删除外键约束
        migrations.RunSQL(
            sql="""
                ALTER TABLE payment_payment DROP CONSTRAINT IF EXISTS payment_payment_wishlist_item_id_fkey;
            """,
            reverse_sql="""
                -- 无需回滚
            """,
        ),
        # 2. 删除原字段
        migrations.RunSQL(
            sql="""
                ALTER TABLE payment_payment DROP COLUMN wishlist_item_id;
            """,
            reverse_sql="""
                -- 无需回滚
            """,
        ),
        # 3. 新增 uuid 字段并恢复外键
        migrations.AddField(
            model_name='payment',
            name='wishlist_item',
            field=models.ForeignKey(
                to='wishlist_new.WishlistItem',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                help_text='Related wishlist item',
                null=True,
                blank=True,
            ),
        ),
    ]
