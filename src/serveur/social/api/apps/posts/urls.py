"""URLs for Posts app"""
from django.urls import path
from .views import (
    PostCreateView,
    PostDetailView,
    PostDeleteView,
    PostFeedView,
    PostDiscoverView
)

urlpatterns = [
    path('create', PostCreateView.as_view(), name='post-create'),
    path('feed', PostFeedView.as_view(), name='post-feed'),
    path('discover', PostDiscoverView.as_view(), name='post-discover'),
    path('<str:id>', PostDetailView.as_view(), name='post-detail'),
    path('<str:id>/delete', PostDeleteView.as_view(), name='post-delete'),
]
