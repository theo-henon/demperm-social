"""
Forums app configuration.
"""
from django.apps import AppConfig


class ForumsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.apps.forums'
    label = 'forums'
