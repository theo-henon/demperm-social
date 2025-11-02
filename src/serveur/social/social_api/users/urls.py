from django.urls import path
from .views import UserMeView, UserDetailView, UserSearchView, UserPostsView

urlpatterns = [
    path('me', UserMeView.as_view(), name='user-me'),  # GET /api/v1/users/me
    path('search', UserSearchView.as_view(), name='user-search'),  # GET /api/v1/users/search
    path('<int:id>', UserDetailView.as_view(), name='user-detail'),  # GET /api/v1/users/:id
    path('<int:id>/posts', UserPostsView.as_view(), name='user-posts'),  # GET /api/v1/users/:id/posts
]