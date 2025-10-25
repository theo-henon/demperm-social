from django.urls import path
from .views import (
    GroupCreateView,
    GroupListView,
    GroupDetailView,
    GroupMembersView
)

urlpatterns = [
    path('', GroupListView.as_view(), name='group-list'),
    path('<int:id>', GroupDetailView.as_view(), name='group-detail'),
    path('<int:id>/members', GroupMembersView.as_view(), name='group-members'),
    path('create', GroupCreateView.as_view(), name='group-create'),
]
