from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0004_add_current_payment_id_field'),
    ]

    operations = [
        # 首先将原字段改名为临时名称
        migrations.RunSQL(
            """
            ALTER TABLE wishlist_wishlistitem 
            RENAME COLUMN current_payment_id TO current_payment_id_old;
            
            -- 创建新UUID字段
            ALTER TABLE wishlist_wishlistitem 
            ADD COLUMN current_payment_id UUID NULL;
            """,
            
            """
            -- 如果需要回滚
            ALTER TABLE wishlist_wishlistitem 
            DROP COLUMN current_payment_id;
            
            ALTER TABLE wishlist_wishlistitem 
            RENAME COLUMN current_payment_id_old TO current_payment_id;
            """
        ),
    ] 