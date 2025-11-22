"""
URL configuration for social_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Social API",
        default_version='v1.0.0',
        description="API du serveur social",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication
    path("api/v1/auth/", include("api.apps.authentication.urls")),
    # Main endpoints
    path("api/v1/users/", include("api.apps.users.urls")),
    path("api/v1/posts/", include("api.apps.posts.urls")),
    path("api/v1/", include("api.apps.followers.urls")),
    path("api/v1/messages/", include("api.apps.messaging.urls")),
    path("api/v1/forums/", include("api.apps.forums.urls")),
    path("api/v1/tags/", include("api.apps.tags.urls")),
    path("api/v1/subscriptions/", include("api.apps.subscriptions.urls")),
    path("api/v1/domains/", include("api.apps.domains.urls")),
    path("api/v1/", include("api.apps.comments.urls")),  # Comments endpoints
    path("api/v1/", include("api.apps.likes.urls")),  # Likes endpoints
    path("api/v1/", include("api.apps.blocks.urls")),  # Blocks endpoints
    path("api/v1/", include("api.apps.reports.urls")),  # Reports endpoints
    path("api/v1/", include("api.apps.admin_panel.urls")),  # Admin endpoints
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
