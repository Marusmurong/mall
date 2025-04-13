from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.urls import reverse
from .models import Wishlist, WishlistItem
from goods.models import Goods
from django.utils import timezone
from django.db import connection
from django.conf import settings
import logging

@login_required
def wishlist_list(request):
    """用户的心愿单列表"""
    wishlists = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/wishlist_list.html', {'wishlists': wishlists})

@login_required
def wishlist_detail(request, wishlist_id):
    """查看心愿单详情"""
    wishlist = get_object_or_404(Wishlist, pk=wishlist_id)
    
    # 添加查看记录
    if request.user.is_authenticated and request.user != wishlist.user:
        # 记录查看者ID，用于通知
        wishlist._viewer_id = request.user.id
        wishlist.save()  # 触发post_save信号
    
    # 使用原始SQL获取心愿单商品
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT wi.id, g.name, g.price, wi.quantity, wi.notes, g.image, g.id as product_id 
            FROM wishlist_wishlistitem wi
            JOIN goods_goods g ON wi.product_id = g.id
            WHERE wi.wishlist_id = %s
            ORDER BY wi.added_at DESC
            """, 
            [wishlist.pk]
        )
        columns = [col[0] for col in cursor.description]
        items = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_public':
            # 切换心愿单公开状态
            wishlist.is_public = request.POST.get('is_public') == 'on'
            wishlist.save()
            status = "公开" if wishlist.is_public else "私密"
            messages.success(request, f'心愿单已设为{status}')
            
        elif action == 'update_quantity':
            # 更新商品数量
            item_id = request.POST.get('item_id')
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE wishlist_wishlistitem 
                        SET quantity = %s 
                        WHERE id = %s AND wishlist_id = %s
                        """, 
                        [quantity, item_id, wishlist.pk]
                    )
                messages.success(request, f'商品数量已更新')
            
        elif action == 'remove_item':
            # 移除商品
            item_id = request.POST.get('item_id')
            # 获取商品名称用于消息提示
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT g.name 
                    FROM wishlist_wishlistitem wi
                    JOIN goods_goods g ON wi.product_id = g.id
                    WHERE wi.id = %s
                    """, 
                    [item_id]
                )
                product_name = cursor.fetchone()[0]
                
                # 删除心愿单商品
                cursor.execute(
                    """
                    DELETE FROM wishlist_wishlistitem 
                    WHERE id = %s AND wishlist_id = %s
                    """, 
                    [item_id, wishlist.pk]
                )
            messages.success(request, f'商品 "{product_name}" 已从心愿单中移除')
            
        elif action == 'update_notes':
            # 更新心愿单备注
            notes = request.POST.get('notes', '')
            wishlist.notes = notes
            wishlist.save()
            messages.success(request, '心愿单备注已更新')
            
        return redirect('wishlist:detail', wishlist_id=wishlist.pk)
    
    context = {
        'wishlist': wishlist,
        'items': items,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'wishlist/wishlist_detail.html', context)

@login_required
def create_wishlist(request):
    """创建新的心愿单"""
    if request.method == 'POST':
        name = request.POST.get('name', '我的心愿单')
        notes = request.POST.get('notes', '')
        is_public = request.POST.get('is_public') == 'on'
        
        wishlist = Wishlist.objects.create(
            name=name,
            user=request.user,
            notes=notes,
            is_public=is_public
        )
        messages.success(request, f'心愿单 "{name}" 创建成功！')
        return redirect('wishlist:detail', wishlist_id=wishlist.pk)
    return render(request, 'wishlist/create_wishlist.html')

@login_required
def add_to_wishlist(request, product_id):
    """将商品添加到心愿单"""
    product = get_object_or_404(Goods, id=product_id)
    
    if request.method == 'POST':
        wishlist_id = request.POST.get('wishlist_id')
        notes = request.POST.get('notes', '')
        
        # 如果用户选择了创建新心愿单
        if wishlist_id == 'new':
            wishlist_name = request.POST.get('new_wishlist_name', '我的心愿单')
            wishlist = Wishlist.objects.create(
                name=wishlist_name,
                user=request.user
            )
        else:
            wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        
        # 从数据库中直接执行SQL语句添加心愿单商品，避开ORM模型映射问题
        with connection.cursor() as cursor:
            # 先检查该商品是否已经在心愿单中
            cursor.execute(
                """
                SELECT id FROM wishlist_wishlistitem 
                WHERE wishlist_id = %s AND product_id = %s
                """, 
                [wishlist.id, product.id]
            )
            existing_item = cursor.fetchone()
            
            if existing_item:
                # 如果商品已存在，更新备注
                cursor.execute(
                    """
                    UPDATE wishlist_wishlistitem 
                    SET notes = %s 
                    WHERE id = %s
                    """, 
                    [notes, existing_item[0]]
                )
            else:
                # 如果商品不存在，创建新记录
                cursor.execute(
                    """
                    INSERT INTO wishlist_wishlistitem 
                    (quantity, added_at, notes, product_id, wishlist_id) 
                    VALUES (1, CURRENT_TIMESTAMP, %s, %s, %s)
                    """, 
                    [notes, product.id, wishlist.id]
                )
        
        messages.success(request, f'商品 "{product.name}" 已添加到心愿单 "{wishlist.name}"')
        return redirect('wishlist:detail', wishlist_id=wishlist.pk)
    
    # 获取用户的所有心愿单
    wishlists = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/add_to_wishlist.html', {
        'product': product,
        'wishlists': wishlists
    })

def share_wishlist(request, share_code):
    """分享心愿单页面"""
    wishlist = get_object_or_404(Wishlist, share_code=share_code)
    
    # 检查心愿单是否为公开状态
    if not wishlist.is_public and (not request.user.is_authenticated or request.user != wishlist.user):
        raise Http404("找不到该心愿单")
    
    # 增加访问量计数（不计算所有者自己的访问）
    if not request.user.is_authenticated or request.user != wishlist.user:
        wishlist.view_count += 1
        wishlist.last_viewed_at = timezone.now()
        wishlist.save(update_fields=['view_count', 'last_viewed_at'])
        
        # 发送Telegram通知给心愿单所有者
        try:
            from telegram_bot.utils import create_notification
            from telegram_bot.models import UserTelegramBinding
            
            # 尝试获取用户的Telegram绑定
            try:
                binding = UserTelegramBinding.objects.get(
                    user=wishlist.user,
                    verified=True,
                    is_active=True
                )
                
                # 构建通知内容
                viewer_name = request.user.username if request.user.is_authenticated else "匿名用户"
                content = f"您的心愿单《{wishlist.name}》刚刚被 {viewer_name} 查看了。\n\n"
                content += f"目前总访问量: {wishlist.view_count}\n"
                content += f"最后访问时间: {wishlist.last_viewed_at.strftime('%Y-%m-%d %H:%M:%S')}"
                
                # 创建并发送通知
                create_notification(
                    binding, 
                    'wishlist_view', 
                    content, 
                    related_object_type='wishlist',
                    related_object_id=wishlist.id
                )
                
                # 异步向Channels组发送通知事件
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer
                
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "telegram_notifications",
                    {
                        'type': 'send_notification',
                        'user_id': wishlist.user.id,
                        'notification_type': 'wishlist_view',
                        'content': content,
                        'related_object_type': 'wishlist',
                        'related_object_id': wishlist.id,
                    }
                )
            except UserTelegramBinding.DoesNotExist:
                # 用户没有绑定Telegram，不发送通知
                pass
        except Exception as e:
            # 发送通知失败不应影响页面正常显示
            logger = logging.getLogger(__name__)
            logger.error(f"发送心愿单查看通知失败: {str(e)}")
    
    # 使用原始SQL获取心愿单商品
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT wi.id, g.name, g.price, wi.quantity, wi.notes, g.image, g.id as product_id 
            FROM wishlist_wishlistitem wi
            JOIN goods_goods g ON wi.product_id = g.id
            WHERE wi.wishlist_id = %s
            ORDER BY wi.added_at DESC
            """, 
            [wishlist.pk]
        )
        columns = [col[0] for col in cursor.description]
        items = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    return render(request, 'wishlist/share_wishlist.html', {
        'wishlist': wishlist, 
        'items': items,
        'MEDIA_URL': settings.MEDIA_URL,
    })

def purchase_item(request, pk):
    """购买心愿单中的物品"""
    item = get_object_or_404(WishlistItem, pk=pk)
    
    if request.method == 'POST':
        # 记录购买者ID，用于通知
        if request.user.is_authenticated:
            item._buyer_id = request.user.id
        
        # 存储先前状态以便检测变化
        item._previous_purchased = item.purchased
        
        # 更改购买状态
        item.purchased = True
        item.purchased_at = timezone.now()
        
        if request.user.is_authenticated:
            item.purchased_by = request.user
        
        item.save()  # 触发post_save信号
        
        messages.success(request, f'商品 "{item.title}" 已标记为已购买')
        return redirect('wishlist:detail', wishlist_id=item.wishlist.pk)
    
    return render(request, 'wishlist/purchase_confirm.html', {'item': item})
