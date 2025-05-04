from django.db import migrations
import os


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_shippingaddress'),  # 更新为最新的迁移依赖
    ]

    def load_sql(apps, schema_editor):
        # 获取迁移文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 读取SQL文件内容
        sql_file = os.path.join(current_dir, 'custom_sql/make_telegram_fields_nullable.sql')
        with open(sql_file, 'r') as f:
            schema_editor.execute(f.read())

    operations = [
        migrations.RunPython(
            code=load_sql,
            reverse_code=migrations.RunPython.noop
        ),
    ] 