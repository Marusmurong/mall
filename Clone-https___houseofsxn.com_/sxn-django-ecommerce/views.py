"""
Views for SXN Django e-commerce project.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import json

# Demo data - In a real project, this would come from a database
CATEGORIES = {
    'fetish-wear': {
        'name': 'Fetish Wear',
        'slug': 'fetish-wear',
        'description': 'Luxury leather fetish wear designed for power, crafted for desire.'
    },
    'lingerie': {
        'name': 'Leather Lingerie',
        'slug': 'lingerie',
        'description': 'Exquisite leather lingerie for a sensual experience.'
    },
    'harness': {
        'name': 'Leather Harness',
        'slug': 'harness',
        'description': 'Stylish leather harnesses to enhance your look.'
    },
    'clothing': {
        'name': 'Coat & Shirts',
        'slug': 'clothing',
        'description': 'High-quality leather coats and shirts.'
    },
    'floggers-whips': {
        'name': 'Floggers & Whips',
        'slug': 'floggers-whips',
        'description': 'Luxury floggers and whips crafted with precision.'
    },
    'impact': {
        'name': 'Impact',
        'slug': 'impact',
        'description': 'Premium impact tools for enthusiasts.'
    },
    'collars': {
        'name': 'Collars & Gags',
        'slug': 'collars',
        'description': 'Elegant collars and gags made with quality materials.'
    },
    'cuffs': {
        'name': 'Restraint & Cuff Sets',
        'slug': 'cuffs',
        'description': 'Premium restraint and cuff sets for your collection.'
    },
    'masks': {
        'name': 'Hoods, Masks and Blindfolds',
        'slug': 'masks',
        'description': 'Luxury hoods, masks and blindfolds crafted with care.'
    },
    'gloves': {
        'name': 'Gloves',
        'slug': 'gloves',
        'description': 'Elegant leather gloves for any occasion.'
    },
    'accessories': {
        'name': 'Leashes, Locks and Accessories',
        'slug': 'accessories',
        'description': 'Complete your collection with our luxury accessories.'
    },
    'couture': {
        'name': 'Runway',
        'slug': 'couture',
        'description': 'Exclusive high-end pieces from our runway collection.'
    }
}

PRODUCTS = [
    {
        'id': 1,
        'name': 'Leather Sense Corsage Lingerie',
        'slug': 'leather-sense-corsage-lingerie',
        'category': 'lingerie',
        'price': 115.00,
        'available_stock': 10,
        'main_image': '/static/img/products/leather-sense-corsage.jpg',
        'second_image': '/static/img/products/leather-sense-corsage-2.jpg',
        'description': 'Provoke or obey with this exclusive, one of a kind black leather lingerie piece. Part of the House of SXN Leather Sense collection, it features an exquisitely soft leather sheepskin upper and bottom merged by a seductively intricate lace flower pattern. Metal studs add a touch of luxury to complete the fetish fashion look.',
        'has_sizes': True
    },
    {
        'id': 2,
        'name': 'VXN Leather and Lace Teddy',
        'slug': 'vxn-leather-lace-teddy',
        'category': 'lingerie',
        'price': 115.00,
        'available_stock': 5,
        'main_image': '/static/img/products/vxn-leather-teddy.jpg',
        'second_image': '/static/img/products/vxn-leather-teddy-2.jpg',
        'description': 'The VXN Leather and Lace Teddy is a luxurious piece that combines the softness of leather with intricate lace detailing. This exclusive design features premium quality materials and expert craftsmanship.',
        'has_sizes': True
    },
    {
        'id': 3,
        'name': 'Leather Sense Skinz Leotard',
        'slug': 'leather-sense-skinz-luxury-lingerie',
        'category': 'lingerie',
        'price': 185.00,
        'available_stock': 0,
        'main_image': '/static/img/products/leather-sense-skinz.jpg',
        'second_image': '/static/img/products/leather-sense-skinz-2.jpg',
        'description': 'The Leather Sense Skinz Leotard is designed to contour your body with premium quality leather that feels like a second skin. This exquisite piece features strategically placed panels that highlight your natural curves.',
        'has_sizes': True
    },
    {
        'id': 4,
        'name': 'Classic Black Leather Corset',
        'slug': 'classic-black-leather-corset',
        'category': 'fetish-wear',
        'price': 150.00,
        'available_stock': 8,
        'main_image': '/static/img/products/classic-leather-corset.jpg',
        'second_image': '/static/img/products/classic-leather-corset-2.jpg',
        'description': 'Our Classic Black Leather Corset is a timeless piece crafted from premium quality leather. The elegant design features steel boning for proper support and shape, while the luxurious leather exterior offers a sleek, sophisticated look.',
        'has_sizes': True
    }
]

# View functions

def home(request):
    """Home page view"""
    # In a real project, you would fetch featured products from a database
    context = {
        'featured_products': PRODUCTS  # In a real project, this would be a query for featured products
    }
    return render(request, 'shop/home.html', context)

def category(request, category_slug):
    """Category page view"""
    # In a real project, you would fetch category data and products from a database
    if category_slug not in CATEGORIES:
        return redirect('home')

    category_data = CATEGORIES[category_slug]

    # Filter products for this category
    category_products = [p for p in PRODUCTS if p['category'] == category_slug]

    context = {
        'category': category_data,
        'products': category_products
    }
    return render(request, 'shop/category.html', context)

def product_detail(request, product_slug):
    """Product detail page view"""
    # In a real project, you would fetch the product data from a database
    product = next((p for p in PRODUCTS if p['slug'] == product_slug), None)

    if not product:
        return redirect('home')

    # Get related products - in a real project this would be more sophisticated
    related_products = [p for p in PRODUCTS if p['category'] == product['category'] and p['id'] != product['id']][:4]

    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'product/product_detail.html', context)

def cart(request):
    """Cart page view"""
    # In a real project, you would fetch the cart items from a session or database
    cart_items = request.session.get('cart_items', [])

    # Calculate cart total - in a real project this would be a db query
    cart_subtotal = sum(float(item.get('total_price', 0)) for item in cart_items)

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal
    }
    return render(request, 'cart/cart.html', context)

@require_POST
def add_to_cart(request, product_id):
    """Add product to cart view"""
    # In a real project, you would add the product to the cart in a session or database
    # This is a simplified example
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return redirect('home')

    quantity = int(request.POST.get('quantity', 1))
    size_id = request.POST.get('size')

    # Check if the product is in stock
    if product['available_stock'] < quantity:
        # In a real project, you would add an error message
        return redirect('product_detail', product_slug=product['slug'])

    # Initialize cart if it doesn't exist
    if 'cart_items' not in request.session:
        request.session['cart_items'] = []

    # Calculate item total price
    total_price = product['price'] * quantity

    # Create cart item
    cart_item = {
        'id': len(request.session['cart_items']) + 1,
        'product_id': product_id,
        'product': product,
        'quantity': quantity,
        'size_id': size_id,
        'size': {'name': 'Medium'} if size_id else None,  # In a real project, you would fetch the size data
        'total_price': total_price
    }

    # Add to cart
    request.session['cart_items'].append(cart_item)
    request.session.modified = True

    # Check if it's a buy now action
    if request.POST.get('buy_now'):
        return redirect('checkout')

    return redirect('cart')

@require_POST
def update_cart(request):
    """Update cart item view"""
    data = json.loads(request.body)
    item_id = int(data.get('item_id'))
    quantity = int(data.get('quantity'))

    # Find and update the cart item
    cart_items = request.session.get('cart_items', [])
    for item in cart_items:
        if item['id'] == item_id:
            item['quantity'] = quantity
            item['total_price'] = item['product']['price'] * quantity
            break

    request.session['cart_items'] = cart_items
    request.session.modified = True

    return JsonResponse({'success': True})

@require_POST
def remove_from_cart(request):
    """Remove item from cart view"""
    data = json.loads(request.body)
    item_id = int(data.get('item_id'))

    # Remove the item from the cart
    cart_items = request.session.get('cart_items', [])
    cart_items = [item for item in cart_items if item['id'] != item_id]

    request.session['cart_items'] = cart_items
    request.session.modified = True

    return JsonResponse({'success': True})

def checkout(request):
    """Checkout page view"""
    # In a real project, you would fetch the cart items from a session or database
    cart_items = request.session.get('cart_items', [])

    # Check if cart is empty
    if not cart_items:
        return redirect('cart')

    # Calculate cart total
    cart_subtotal = sum(float(item.get('total_price', 0)) for item in cart_items)

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'special_instructions': request.GET.get('instructions', '')
    }
    return render(request, 'cart/checkout.html', context)

# Account views
def account(request):
    """Account page view"""
    # In a real project, you would check if the user is authenticated
    return render(request, 'account/account.html')

def login(request):
    """Login page view"""
    return render(request, 'account/login.html')

def register(request):
    """Register page view"""
    return render(request, 'account/register.html')

def logout(request):
    """Logout view"""
    # In a real project, you would log the user out
    return redirect('home')

# Static pages
def about(request):
    """About page view"""
    return render(request, 'pages/about.html')

def contact(request):
    """Contact page view"""
    return render(request, 'pages/contact.html')

def lookbooks(request):
    """Lookbooks page view"""
    return render(request, 'pages/lookbooks.html')

def events(request):
    """Events page view"""
    return render(request, 'pages/events.html')

# Info pages
def delivery(request):
    """Delivery page view"""
    return render(request, 'pages/delivery.html')

def returns(request):
    """Returns page view"""
    return render(request, 'pages/returns.html')

def faqs(request):
    """FAQs page view"""
    return render(request, 'pages/faqs.html')

def alliances(request):
    """Alliances page view"""
    return render(request, 'pages/alliances.html')

def disclaimer(request):
    """Disclaimer page view"""
    return render(request, 'pages/disclaimer.html')

def ada_statement(request):
    """ADA Statement page view"""
    return render(request, 'pages/ada_statement.html')

def privacy_policy(request):
    """Privacy Policy page view"""
    return render(request, 'pages/privacy_policy.html')

def terms(request):
    """Terms and Conditions page view"""
    return render(request, 'pages/terms.html')

# API endpoints
@require_POST
def newsletter_signup(request):
    """Newsletter signup API endpoint"""
    # In a real project, you would save the email to a database or send it to a newsletter service
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'success': False, 'error': 'Email is required'})

    # Placeholder for success response
    return JsonResponse({'success': True})

@require_POST
def product_question(request, product_id):
    """Product question API endpoint"""
    # In a real project, you would save the question to a database or send it to a customer service system
    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('message')

    if not all([name, email, message]):
        return JsonResponse({'success': False, 'error': 'All fields are required'})

    # Placeholder for success response
    return JsonResponse({'success': True})
