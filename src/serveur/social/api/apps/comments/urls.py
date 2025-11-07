from django.urls import path
from .views import (
    TopicCommentCreateView,
    TopicCommentListView,
    CommentLikeView,
    CommentDeleteView
)

urlpatterns = [
    path('topics/<int:id>/comments', TopicCommentListView.as_view(), name='topic-comments-list'),  # GET /api/v1/topics/:id/comments
    path('topics/<int:id>/comments/add', TopicCommentCreateView.as_view(), name='topic-comments-add'),  # POST /api/v1/topics/:id/comments/add
    path('comments/<int:id>/like', CommentLikeView.as_view(), name='comment-like'),  # POST /api/v1/comments/:id/like
    path('comments/<int:id>/delete', CommentDeleteView.as_view(), name='comment-delete'),  # DELETE /api/v1/comments/:id/delete
]
