"""URLs for Forums app"""
from django.urls import path
from .views import (
    ForumsListView,
    ForumCreateView,
    ForumDetailView,
    ForumSubforumsListView,
    ForumSubforumCreateView,
    ForumMeView,
    ForumSearchView
)

urlpatterns = [
    path('', ForumsListView.as_view(), name='forums-list'),
    path('create', ForumCreateView.as_view(), name='forum-create'),
    path('me', ForumMeView.as_view(), name='forum-me'),
    path('search', ForumSearchView.as_view(), name='forum-search'),
    path('<str:id>', ForumDetailView.as_view(), name='forum-detail'),
    path('<str:id>/subforums', ForumSubforumsListView.as_view(), name='forum-subforums'),
    path('<str:id>/subforums/create', ForumSubforumCreateView.as_view(), name='subforum-create'),
]
