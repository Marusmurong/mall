from django.contrib import admin
from .models import 商品分类, 商品

# 注册商品分类模型
@admin.register(商品分类)
class 商品分类Admin(admin.ModelAdmin):
    list_display = ['名称', '父类', '级别', '是否启用', '排序', '创建时间']
    list_filter = ['级别', '是否启用']
    search_fields = ['名称']
    list_editable = ['排序', '是否启用']
    ordering = ['排序']


# 注册商品模型
@admin.register(商品)
class 商品Admin(admin.ModelAdmin):
    list_display = ['名称', '分类', '价格', '原价', '库存', '销量', 
                   '状态', '是否推荐', '是否热门', '是否新品', '创建时间']
    list_filter = ['分类', '状态', '是否推荐', '是否热门', '是否新品']
    search_fields = ['名称', '描述']
    list_editable = ['价格', '库存', '状态', '是否推荐', '是否热门', '是否新品']
    readonly_fields = ['销量', '创建时间', '更新时间']
    fieldsets = (
        ('基本信息', {
            'fields': ('名称', '分类', '主图', '描述')
        }),
        ('价格与库存', {
            'fields': ('价格', '原价', '库存', '销量')
        }),
        ('商品状态', {
            'fields': ('状态', '是否推荐', '是否热门', '是否新品')
        }),
        ('时间信息', {
            'fields': ('创建时间', '更新时间')
        }),
    ) 