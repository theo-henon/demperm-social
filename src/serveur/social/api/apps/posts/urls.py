from django.urls import path
from .views import PostCreateView, PostDetailView, PostDeleteView, PostFeedView, PostDiscoverView

urlpatterns = [
    path('create', PostCreateView.as_view(), name='post-create'),  # POST /api/v1/posts/create
    path('<int:id>', PostDetailView.as_view(), name='post-detail'),  # GET /api/v1/posts/:id
    path('<int:id>/delete', PostDeleteView.as_view(), name='post-delete'),  # DELETE /api/v1/posts/:id/delete
    path('feed', PostFeedView.as_view(), name='post-feed'),  # GET /api/v1/posts/feed
    path('discover', PostDiscoverView.as_view(), name='post-discover'),  # GET /api/v1/posts/discover
]
