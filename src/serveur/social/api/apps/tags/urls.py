"""URLs for Tags app"""
from django.urls import path
from .views import TagsListView, TagCreateView, TagAssignView, TagUnassignView, TagDeleteView

urlpatterns = [
    path('', TagsListView.as_view(), name='tags-list'),
    path('create', TagCreateView.as_view(), name='tag-create'),
    path('assign/<str:post_id>', TagAssignView.as_view(), name='tag-assign'),
    path('unassign/<str:post_id>', TagUnassignView.as_view(), name='tag-unassign'),
    path('delete', TagDeleteView.as_view(), name='tag-delete'),
]
