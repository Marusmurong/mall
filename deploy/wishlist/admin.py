from django.contrib import admin
from .models import Wishlist, WishlistItem

# 注意：此应用已被弃用，请使用 wishlist_new 应用
# 所有管理界面配置已移至 wishlist_new/admin.py

class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 1

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'view_count', 'last_viewed_at', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'user__username')
    readonly_fields = ('view_count', 'last_viewed_at')
    inlines = [WishlistItemInline]

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'wishlist', 'price', 'currency', 'priority', 'purchased', 'created_at')
    list_filter = ('created_at', 'purchased', 'priority', 'currency')
    search_fields = ('title', 'description', 'wishlist__name')
    raw_id_fields = ('wishlist', 'purchased_by')
