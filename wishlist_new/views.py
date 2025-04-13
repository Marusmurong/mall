from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Wishlist, WishlistItem
from goods.models import Goods

@login_required
def wishlist_list(request):
    """显示用户的心愿单列表"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'wishlist_new/wishlist.html', {'wishlist': wishlist})

@login_required
def add_to_wishlist(request):
    """添加商品到心愿单"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if product_id:
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            product = get_object_or_404(Goods, id=product_id)
            WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def remove_from_wishlist(request, item_id):
    """从心愿单中移除商品"""
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    return redirect('wishlist_new:list')
