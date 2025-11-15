from django.urls import path
from .views import (
    ForumListView, ForumCreateView, ForumDetailView, ForumMeView,
    ForumSearchView, ForumSubforumsView, ForumSubforumCreateView
)

urlpatterns = [
    path('', ForumListView.as_view(), name='forum-list'),  # GET /api/v1/forums
    path('create', ForumCreateView.as_view(), name='forum-create'),  # POST /api/v1/forums/create
    path('me', ForumMeView.as_view(), name='forum-me'),  # GET /api/v1/forums/me
    path('search', ForumSearchView.as_view(), name='forum-search'),  # GET /api/v1/forums/search
    path('<uuid:id>', ForumDetailView.as_view(), name='forum-detail'),  # GET /api/v1/forums/:id
    path('<uuid:id>/subforums', ForumSubforumsView.as_view(), name='forum-subforums'),  # GET /api/v1/forums/:id/subforums
    path('<uuid:id>/subforums/create', ForumSubforumCreateView.as_view(), name='forum-subforum-create'),  # POST /api/v1/forums/:id/subforums/create
]
