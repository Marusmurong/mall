# House of SXN - Django E-commerce Project Structure

This document outlines the recommended structure for integrating the HTML templates with Django.

## Django Project Structure

```
sxn_ecommerce/
├── manage.py
├── sxn_ecommerce/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── static/
│   ├── css/
│   ├── js/
│   ├── img/
│   └── video/
├── templates/
│   ├── base/
│   ├── shop/
│   ├── product/
│   ├── cart/
│   └── account/
├── shop/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── product/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── cart/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
└── account/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── migrations/
```

## Django Models

### Shop App Models

```python
# shop/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### Product App Models

```python
# product/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from shop.models import Category

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    main_image = models.ImageField(upload_to='products/')
    second_image = models.ImageField(upload_to='products/', blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_stock = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    has_sizes = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product.name}"

class Size(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.size.name}"
```

### Cart App Models

```python
# cart/models.py
from django.db import models
from django.conf import settings
from product.models import Product, ProductSize

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def total(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity
```

## Django Views

### Shop App Views

```python
# shop/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from product.models import Product, Category

def home(request):
    featured_products = Product.objects.filter(available_stock__gt=0)[:8]
    return render(request, 'shop/home.html', {
        'featured_products': featured_products
    })

class CategoryListView(ListView):
    model = Category
    template_name = 'shop/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'shop/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(available_stock__gt=0)
        return context
```

### Product App Views

```python
# product/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.http import JsonResponse
from .models import Product

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get related products
        related_products = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]

        context['related_products'] = related_products
        return context

def product_question(request, product_id):
    if request.method == 'POST':
        # Handle question submission
        # In a real app, save to database

        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=405)
```

### Cart App Views

```python
# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from product.models import Product, ProductSize
import json

def get_or_create_cart(request):
    """Helper function to get or create a cart"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_id=session_id)

    return cart

def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart.html', {
        'cart_items': cart.items.all(),
        'cart_subtotal': cart.total
    })

@require_POST
def add_to_cart(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    data = json.loads(request.body) if request.body else {}
    quantity = data.get('quantity', 1)
    size_id = data.get('size')

    size = None
    if size_id and product.has_sizes:
        size = get_object_or_404(ProductSize, id=size_id, product=product)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Handle 'buy_now' parameter
    if data.get('buy_now'):
        return redirect('checkout')

    return JsonResponse({'success': True})

@require_POST
def update_cart(request):
    data = json.loads(request.body)
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.quantity = quantity
        cart_item.save()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@require_POST
def remove_from_cart(request):
    data = json.loads(request.body)
    item_id = data.get('item_id')

    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
```

## Django URLs

### Main Project URLs

```python
# sxn_ecommerce/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('products/', include('product.urls')),
    path('cart/', include('cart.urls')),
    path('account/', include('account.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### Shop App URLs

```python
# shop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),
    path('lookbooks/', views.lookbooks, name='lookbooks'),
    path('events/', views.events, name='events'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    # Legal pages
    path('delivery/', views.delivery, name='delivery'),
    path('returns/', views.returns, name='returns'),
    path('faqs/', views.faqs, name='faqs'),
    path('alliances/', views.alliances, name='alliances'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('ada-statement/', views.ada_statement, name='ada_statement'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
]
```

### Product App URLs

```python
# product/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('question/<int:product_id>/', views.product_question, name='product_question'),
]
```

### Cart App URLs

```python
# cart/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart, name='update_cart'),
    path('remove/', views.remove_from_cart, name='remove_from_cart'),
]
```

## Integration Steps

1. Create a new Django project:
   ```
   django-admin startproject sxn_ecommerce
   ```

2. Create the required apps:
   ```
   cd sxn_ecommerce
   python manage.py startapp shop
   python manage.py startapp product
   python manage.py startapp cart
   python manage.py startapp account
   ```

3. Copy the template files to the Django project:
   - Copy the HTML files to their respective folders in the templates directory
   - Copy the static files (CSS, JS, images, video) to the static directory

4. Configure Django settings:
   ```python
   # sxn_ecommerce/settings.py

   INSTALLED_APPS = [
       # Django default apps
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',

       # Custom apps
       'shop',
       'product',
       'cart',
       'account',

       # Third-party apps
       'crispy_forms',
   ]

   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [BASE_DIR / 'templates'],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
               ],
           },
       },
   ]

   STATIC_URL = '/static/'
   STATICFILES_DIRS = [BASE_DIR / 'static']
   STATIC_ROOT = BASE_DIR / 'staticfiles'

   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   ```

5. Create the database models:
   - Implement the models as described above
   - Run migrations:
     ```
     python manage.py makemigrations
     python manage.py migrate
     ```

6. Implement the views and URLs:
   - Create the views and URL patterns as shown above
   - Make sure all URL names referenced in templates are defined

7. Test and run the server:
   ```
   python manage.py runserver
   ```

## Additional Features to Implement

1. Authentication system:
   - User registration, login, password reset
   - User profile with order history

2. Order processing:
   - Checkout process
   - Payment gateway integration
   - Order confirmation and tracking

3. Admin interface customization:
   - Custom admin views for product management
   - Dashboard for sales and inventory tracking

4. Search functionality:
   - Product search with filters
   - Category and tag-based filtering

5. Reviews and ratings:
   - Allow customers to leave reviews and ratings for products

6. Wishlist functionality:
   - Allow customers to save products to a wishlist

7. Responsive design improvements:
   - Mobile-specific optimizations
   - Touch-friendly interfaces

8. Performance optimizations:
   - Caching
   - Database query optimization
   - Image optimization
