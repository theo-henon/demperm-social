"""
URL patterns for comments endpoints.
"""
from django.urls import path
from .views import (
    PostCommentsListView,
    PostCommentCreateView,
    CommentDeleteView,
    CommentRepliesListView,
    CommentReplyView
)

urlpatterns = [
    # Post comments
    path('posts/<uuid:post_id>/comments', PostCommentsListView.as_view(), name='post-comments-list'),
    path('posts/<uuid:post_id>/comments/create', PostCommentCreateView.as_view(), name='post-comment-create'),
    
    # Comment management
    path('comments/<uuid:comment_id>/delete', CommentDeleteView.as_view(), name='comment-delete'),
    path('comments/<uuid:comment_id>/replies', CommentRepliesListView.as_view(), name='comment-replies'),
    path('comments/<uuid:comment_id>/reply', CommentReplyView.as_view(), name='comment-reply'),
]
