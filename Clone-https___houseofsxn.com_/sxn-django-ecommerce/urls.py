"""
URL Configuration for SXN Django e-commerce project.
"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Shop pages
    path('category/<slug:category_slug>/', views.category, name='category'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),

    # Cart pages
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Account pages
    path('account/', views.account, name='account'),
    path('account/login/', views.login, name='login'),
    path('account/register/', views.register, name='register'),
    path('account/logout/', views.logout, name='logout'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('lookbooks/', views.lookbooks, name='lookbooks'),
    path('events/', views.events, name='events'),

    # Info pages
    path('delivery/', views.delivery, name='delivery'),
    path('returns/', views.returns, name='returns'),
    path('faqs/', views.faqs, name='faqs'),
    path('alliances/', views.alliances, name='alliances'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('ada-statement/', views.ada_statement, name='ada_statement'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),

    # API endpoints
    path('api/newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('api/product-question/<int:product_id>/', views.product_question, name='product_question'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
