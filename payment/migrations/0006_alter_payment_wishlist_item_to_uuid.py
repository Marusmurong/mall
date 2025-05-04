from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('wishlist_new', '0001_initial'),
        ('payment', '0003_auto_20250330_1049'),
    ]

    operations = [
        migrations.AlterField(
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
