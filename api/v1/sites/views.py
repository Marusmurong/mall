from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from mall.settings import SITE_NAMES
import json
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def site_config(request, site_id):
    """
    Get site configuration information
    
    This API is used to get configuration information for a specified site, including themes, features, etc.
    """
    # Check if site ID is valid
    if site_id not in SITE_NAMES:
        return Response(
            {"error": f"Site ID '{site_id}' does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get site configuration from database or cache
    # This is a simple example, in actual applications it should be read from the database
    site_config = {
        'id': site_id,
        'name': SITE_NAMES.get(site_id, 'Default Mall'),
        'theme': 'default',
        'features': {
            'wishlist': True,
            'cart': True,
            'user_profile': True,
            'multi_currency': False,
            'live_chat': False
        },
        'layout': {
            'header_style': 'standard',
            'footer_style': 'standard',
            'sidebar_position': 'left'
        },
        'colors': {
            'primary': '#3490dc',
            'secondary': '#ffed4a',
            'accent': '#f66d9b',
            'background': '#f8fafc',
            'text': '#22292f'
        },
        'fonts': {
            'heading': 'Roboto, sans-serif',
            'body': 'Open Sans, sans-serif'
        },
        'localization': {
            'default_language': 'en-US',
            'available_languages': ['en-US', 'zh-CN'],
            'default_currency': 'USD',
            'available_currencies': ['USD', 'CNY']
        }
    }
    
    logger.info(f"Providing configuration information for site '{site_id}'")
    return Response(site_config)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_sites(request):
    """
    Get a list of all available sites
    
    This API is used to get information on all available sites in the system
    """
    sites = []
    for site_id, site_name in SITE_NAMES.items():
        sites.append({
            'id': site_id,
            'name': site_name,
            'url': f'/?site={site_id}',
            'description': f'{site_name} mall, offering high-quality {site_name} related products.'
        })
    
    logger.info(f"Providing site list, total {len(sites)} sites")
    return Response(sites)

@api_view(['GET'])
@permission_classes([AllowAny])
def site_statistics(request, site_id):
    """
    Get site statistics
    
    This API is used to get statistics for a specified site
    """
    # Check if site ID is valid
    if site_id not in SITE_NAMES:
        return Response(
            {"error": f"Site ID '{site_id}' does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Example data, in actual applications it should be queried from the database
    statistics = {
        'visitors': {
            'today': 1245,
            'yesterday': 1043,
            'this_week': 6789,
            'this_month': 24567
        },
        'orders': {
            'today': 37,
            'yesterday': 42,
            'this_week': 245,
            'this_month': 987
        },
        'revenue': {
            'today': 12450.78,
            'yesterday': 15678.92,
            'this_week': 78901.45,
            'this_month': 324567.89
        },
        'popular_products': [
            {'id': 1, 'name': 'Product 1', 'sales': 245},
            {'id': 2, 'name': 'Product 2', 'sales': 198},
            {'id': 3, 'name': 'Product 3', 'sales': 156}
        ]
    }
    
    logger.info(f"Providing statistics for site '{site_id}'")
    return Response(statistics) 