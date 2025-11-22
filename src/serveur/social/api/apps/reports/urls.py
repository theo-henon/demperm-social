"""
URL patterns for reports endpoints.
"""
from django.urls import path
from .views import ReportCreateView

urlpatterns = [
    path('reports/create', ReportCreateView.as_view(), name='report-create'),
]
