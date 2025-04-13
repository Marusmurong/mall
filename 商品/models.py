from django.db import models

# 商品分类模型
class 商品分类(models.Model):
    名称 = models.CharField(max_length=100, verbose_name='分类名称')
    父类 = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父级分类', related_name='子类')
    级别 = models.PositiveIntegerField(default=1, verbose_name='分类级别')
    是否启用 = models.BooleanField(default=True, verbose_name='是否启用')
    排序 = models.PositiveIntegerField(default=0, verbose_name='排序')
    创建时间 = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name
        ordering = ['排序']

    def __str__(self):
        return self.名称


# 商品模型
class 商品(models.Model):
    状态选项 = [
        ('草稿', '草稿'),
        ('已发布', '已发布'),
        ('已售罄', '已售罄'),
        ('已下架', '已下架'),
    ]
    
    名称 = models.CharField(max_length=200, verbose_name='商品名称')
    分类 = models.ForeignKey(商品分类, on_delete=models.CASCADE, verbose_name='商品分类', related_name='商品')
    价格 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    原价 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    库存 = models.PositiveIntegerField(default=0, verbose_name='库存')
    销量 = models.PositiveIntegerField(default=0, verbose_name='销量')
    主图 = models.ImageField(upload_to='商品/图片/', null=True, blank=True, verbose_name='主图')
    描述 = models.TextField(blank=True, verbose_name='商品描述')
    状态 = models.CharField(max_length=20, choices=状态选项, default='草稿', verbose_name='状态')
    是否推荐 = models.BooleanField(default=False, verbose_name='是否推荐')
    是否热门 = models.BooleanField(default=False, verbose_name='是否热门')
    是否新品 = models.BooleanField(default=True, verbose_name='是否新品')
    创建时间 = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    更新时间 = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ['-创建时间']

    def __str__(self):
        return self.名称 