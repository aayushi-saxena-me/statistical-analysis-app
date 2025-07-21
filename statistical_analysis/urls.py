from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection
import os

def health_check(request):
    """Health check endpoint for Docker"""
    return JsonResponse({'status': 'healthy', 'service': 'statistical_analysis'})

def simple_test(request):
    """Ultra simple test - no database, no imports"""
    import os
    return JsonResponse({
        'test': 'working',
        'django_settings_module': os.environ.get('DJANGO_SETTINGS_MODULE'),
        'database_url_exists': 'DATABASE_URL' in os.environ,
        'database_url_value': os.environ.get('DATABASE_URL', 'NOT_SET')[:50] + '...' if os.environ.get('DATABASE_URL') else 'NOT_SET'
    })

def db_test(request):
    """Test database connection"""
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        db_info = connection.settings_dict
        return JsonResponse({
            'database_connected': True,
            'engine': db_info.get('ENGINE'),
            'name': db_info.get('NAME'),
            'host': db_info.get('HOST', 'localhost'),
            'database_url_set': bool(os.environ.get('DATABASE_URL')),
            'test_result': result[0] if result else None
        })
    except Exception as e:
        return JsonResponse({
            'database_connected': False,
            'error': str(e),
            'database_url_set': bool(os.environ.get('DATABASE_URL'))
        })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('simple-test/', simple_test, name='simple_test'),
    path('db-test/', db_test, name='db_test'),
    path('', include('analysis.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
