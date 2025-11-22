"""URLs for Users app"""
from django.urls import path
from .views import (
    UserMeView,
    UserSettingsView,
    UserDetailView,
    UserSearchView,
    UserBulkView,
    UserDiscoverView,
    UserPostsView,
    UserPublicKeyView,
    UserPublicKeyUploadView
)

urlpatterns = [
    path('me', UserMeView.as_view(), name='user-me'),
    path('me/settings', UserSettingsView.as_view(), name='user-settings'),
    path('me/public_key', UserPublicKeyUploadView.as_view(), name='user-public-key-upload'),
    path('search', UserSearchView.as_view(), name='user-search'),
    path('bulk', UserBulkView.as_view(), name='user-bulk'),
    path('discover', UserDiscoverView.as_view(), name='user-discover'),
    path('<str:id>', UserDetailView.as_view(), name='user-detail'),
    path('<str:id>/posts', UserPostsView.as_view(), name='user-posts'),
    path('<str:id>/public_key', UserPublicKeyView.as_view(), name='user-public-key'),
]
