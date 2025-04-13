from django.contrib import admin
from .models import Wishlist, WishlistItem

class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 1

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'user__username')
    inlines = [WishlistItemInline]

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'wishlist', 'price', 'currency', 'priority', 'purchased', 'created_at')
    list_filter = ('created_at', 'purchased', 'priority', 'currency')
    search_fields = ('title', 'description', 'wishlist__name')
    raw_id_fields = ('wishlist', 'purchased_by')
