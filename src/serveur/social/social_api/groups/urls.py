from django.urls import path
from .views import (
    GroupCreateView,
    GroupListView,
    GroupDetailView,
    GroupMembersView
)

urlpatterns = [
    path('', GroupListView.as_view(), name='group-list'),  # GET /api/v1/groups
    path('<int:id>', GroupDetailView.as_view(), name='group-detail'),  # GET /api/v1/groups/:id
    path('<int:id>/members', GroupMembersView.as_view(), name='group-members'),  # GET /api/v1/groups/:id/members
    path('create', GroupCreateView.as_view(), name='group-create'),  # POST /api/v1/groups/create
]
