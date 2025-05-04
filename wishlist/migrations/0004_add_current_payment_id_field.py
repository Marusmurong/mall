from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0003_wishlist_last_viewed_at_wishlist_view_count'),  # 确保依赖于前一个迁移
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE wishlist_wishlistitem ADD COLUMN IF NOT EXISTS current_payment_id INTEGER NULL;",
            "ALTER TABLE wishlist_wishlistitem DROP COLUMN IF EXISTS current_payment_id;"
        ),
    ] 