"""
URL patterns for likes endpoints.
"""
from django.urls import path
from .views import PostLikeView, PostUnlikeView, PostLikesListView

urlpatterns = [
    path('posts/<uuid:post_id>/like', PostLikeView.as_view(), name='post-like'),
    path('posts/<uuid:post_id>/unlike', PostUnlikeView.as_view(), name='post-unlike'),
    path('posts/<uuid:post_id>/likes', PostLikesListView.as_view(), name='post-likes-list'),
]
