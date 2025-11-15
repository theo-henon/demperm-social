from django.urls import path
from .views import (
    PostCreateView, PostDetailView, PostUpdateView, PostDeleteView,
    PostFeedView, PostDiscoverView
)

urlpatterns = [
    path('create', PostCreateView.as_view(), name='post-create'),  # POST /api/v1/posts/create
    path('feed', PostFeedView.as_view(), name='post-feed'),  # GET /api/v1/posts/feed
    path('discover', PostDiscoverView.as_view(), name='post-discover'),  # GET /api/v1/posts/discover
    path('<uuid:id>', PostDetailView.as_view(), name='post-detail'),  # GET /api/v1/posts/:id
    path('<uuid:id>/update', PostUpdateView.as_view(), name='post-update'),  # PATCH /api/v1/posts/:id/update
    path('<uuid:id>/delete', PostDeleteView.as_view(), name='post-delete'),  # DELETE /api/v1/posts/:id/delete
]
