import uuid
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from goods.models import Goods

User = get_user_model()

class Wishlist(models.Model):
    """Wishlist"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User')
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_public = models.BooleanField(default=True, verbose_name=_('Is Public'))
    share_code = models.CharField(max_length=20, unique=True, blank=True, verbose_name=_('Share Code'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.user.username}\'s Wishlist'
    
    def save(self, *args, **kwargs):
        if not self.share_code:
            self.share_code = self.generate_share_code()
        super().save(*args, **kwargs)
    
    def generate_share_code(self):
        """Generate share code"""
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Check if already exists
        while Wishlist.objects.filter(share_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return code
    
    def get_absolute_url(self):
        return reverse('wishlist_detail', args=[str(self.id)])
    
    def get_share_url(self):
        return reverse('wishlist_share', args=[self.share_code])
        
    def get_view_count(self):
        """Get wishlist view count"""
        return self.views.count()


class WishlistItem(models.Model):
    """Wishlist Item"""
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items', verbose_name='Wishlist')
    # Temporarily make product field optional for migration
    product = models.ForeignKey(Goods, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Product')
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    image = models.ImageField(upload_to='wishlist_items/', blank=True, null=True, verbose_name=_('Image'))
    url = models.URLField(blank=True, verbose_name=_('URL'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('Priority'))
    
    # Purchase related fields
    purchased = models.BooleanField(default=False, verbose_name=_('Purchased'))
    purchased_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Purchase Time'))
    purchased_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='purchased_items_new', verbose_name=_('Purchaser'))
    
    # Payment related fields
    current_payment = models.ForeignKey('payment.Payment', null=True, blank=True, on_delete=models.SET_NULL, related_name='current_item_new', verbose_name=_('Current Payment'))
    payment_status = models.CharField(max_length=20, blank=True, verbose_name=_('Payment Status'))
    payment_completed = models.BooleanField(default=False, verbose_name=_('Payment Completed'))
    
    # Temporarily remove auto_now_add and set default value for migration
    added_at = models.DateTimeField(default=timezone.now, verbose_name='Added At')
    
    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = verbose_name
        ordering = ['-added_at', 'priority']
        # Temporarily comment out unique_together constraint to resolve migration issues
        # unique_together = ('wishlist', 'product')
        
    def __str__(self):
        product_name = self.product.name if self.product else 'Unspecified Product'
        return f'{self.wishlist.user.username}\'s Wishlist - {product_name}'
    
    def formatted_price(self):
        return f"{self.price} {self.currency}"
    
    def get_absolute_url(self):
        return reverse('wishlist_detail', args=[str(self.wishlist.id)])


class WishlistView(models.Model):
    """Wishlist View Record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='views', verbose_name='Wishlist')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='User')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='View Time')
    
    class Meta:
        verbose_name = 'Wishlist View Record'
        verbose_name_plural = verbose_name
        ordering = ['-viewed_at']
        
    def __str__(self):
        return f'{self.wishlist} - {self.viewed_at}'
