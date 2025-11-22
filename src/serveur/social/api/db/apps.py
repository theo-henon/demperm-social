"""
Database app configuration.
Contains all Django ORM entities and migrations.
"""
from django.apps import AppConfig


class DbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.db'
    label = 'db'
    verbose_name = 'Database Layer'
