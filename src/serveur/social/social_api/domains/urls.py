"""URLs for Domains app"""
from django.urls import path
from .views import DomainsListView, DomainDetailView, DomainSubforumsView, DomainSubforumCreateView

urlpatterns = [
    path('', DomainsListView.as_view(), name='domains-list'),
    path('<str:id>', DomainDetailView.as_view(), name='domain-detail'),
    path('<str:id>/subforums', DomainSubforumsView.as_view(), name='domain-subforums'),
    path('<str:id>/subforums/create', DomainSubforumCreateView.as_view(), name='domain-subforum-create'),
]
