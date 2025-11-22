"""
URL patterns for blocks endpoints.
"""
from django.urls import path
from .views import UserBlockView, UserUnblockView, BlockedUsersListView

urlpatterns = [
    path('users/<uuid:user_id>/block', UserBlockView.as_view(), name='user-block'),
    path('users/<uuid:user_id>/unblock', UserUnblockView.as_view(), name='user-unblock'),
    path('users/me/blocked', BlockedUsersListView.as_view(), name='blocked-users-list'),
]
