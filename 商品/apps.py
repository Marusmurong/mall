from django.apps import AppConfig


class 商品Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '商品'
    verbose_name = '商品管理' 