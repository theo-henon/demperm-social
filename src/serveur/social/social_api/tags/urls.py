from django.urls import path
from .views import TagCreateView, TagListView, AssignTagsToTopicView

urlpatterns = [
    path('', TagListView.as_view(), name='tag-list'),  # GET /api/v1/tags
    path('create', TagCreateView.as_view(), name='tag-create'),  # POST /api/v1/tags/create
    path('assign/<int:post_id>', AssignTagsToTopicView.as_view(), name='tag-assign'),  # POST /api/v1/tags/assign/:post_id
]