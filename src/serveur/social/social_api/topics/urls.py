from django.urls import path
from .views import (
    TopicCreateView,
    TopicListView,
    TopicDetailView,
    TopicDeleteView
)

urlpatterns = [
    path('', TopicListView.as_view(), name='topic-list'),           # GET /api/v1/topics
    path('create', TopicCreateView.as_view(), name='topic-create'), # POST /api/v1/topics
    path('<int:id>', TopicDetailView.as_view(), name='topic-detail'), # GET /api/v1/topics/:id
    path('<int:id>/delete', TopicDeleteView.as_view(), name='topic-delete') # DELETE /api/v1/topics/:id
]