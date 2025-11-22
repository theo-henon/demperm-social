"""
Followers app configuration.
"""
from django.apps import AppConfig


class FollowersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.apps.followers'
    label = 'followers'
