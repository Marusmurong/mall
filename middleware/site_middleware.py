from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import threading

# Global thread local storage for storing current site information during request processing
_thread_local = threading.local()

class SiteMiddleware(MiddlewareMixin):
    """
    Middleware to detect the current site of the request
    """
    
    def process_request(self, request):
        """
        Process each request, determine the current site and store it in thread local variable
        """
        # Always use 'default' site
        current_site = 'default'
        
        # Store the current site in thread local variable
        _thread_local.current_site = current_site
        
        # Add the current site to the request object for use in views
        request.current_site = current_site
        
        # Middleware doesn't need to return any response, continue processing the request


def get_current_site():
    """
    Get the current site of the request
    Can be used in models, views, templates, etc.
    """
    return getattr(_thread_local, 'current_site', 'default')
