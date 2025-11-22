"""
URL configuration for demperm-social backend.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions

# drf_yasg imports can trigger DRF settings to import third-party auth classes
# which may import Django models before apps are ready. To avoid AppRegistry
# errors at import time, import drf_yasg lazily when the docs endpoint is hit.
def _get_schema_view():
    """Lazily create and return a drf_yasg schema view.

    This defers importing drf_yasg until a request reaches the docs endpoints,
    avoiding import-time issues with Django app registry.
    """
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    return get_schema_view(
        openapi.Info(
            title="Demperm Social API",
            default_version='v1',
            description="API REST pour réseau social politique local",
            terms_of_service="https://www.example.com/terms/",
            contact=openapi.Contact(email="contact@example.com"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

def _swagger_view(request, *args, **kwargs):
    """View wrapper for Swagger UI that instantiates schema view lazily."""
    return _get_schema_view().with_ui('swagger', cache_timeout=0)(request, *args, **kwargs)

def _redoc_view(request, *args, **kwargs):
    """View wrapper for ReDoc UI that instantiates schema view lazily."""
    return _get_schema_view().with_ui('redoc', cache_timeout=0)(request, *args, **kwargs)

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/auth/', include('apps.custom_auth.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/domains/', include('apps.domains.urls')),
    path('api/v1/forums/', include('apps.forums.urls')),
    path('api/v1/subforums/', include('apps.subforums.urls')),
    path('api/v1/subscriptions/', include('apps.subscriptions.urls')),
    path('api/v1/posts/', include('apps.posts.urls')),
    path('api/v1/comments/', include('apps.comments.urls')),
    path('api/v1/likes/', include('apps.likes.urls')),
    path('api/v1/followers/', include('apps.followers.urls')),
    path('api/v1/following/', include('apps.followers.urls')),  # Alias
    path('api/v1/tags/', include('apps.tags.urls')),
    path('api/v1/messages/', include('apps.custom_messages.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/admin/', include('apps.admin_panel.urls')),
    
    # API Documentation
    path('api/v1/docs/', _swagger_view, name='schema-swagger-ui'),
    path('api/v1/redoc/', _redoc_view, name='schema-redoc'),
]

