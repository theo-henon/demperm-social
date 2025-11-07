from django.urls import path
from .views import TagCreateView, TagListView, AssignTagsToPostView, UnassignTagsFromPostView, TagDeleteView

urlpatterns = [
    path('', TagListView.as_view(), name='tag-list'),  # GET /api/v1/tags
    path('create', TagCreateView.as_view(), name='tag-create'),  # POST /api/v1/tags/create
    path('assign/<int:post_id>', AssignTagsToPostView.as_view(), name='tag-assign'),  # POST /api/v1/tags/assign/:post_id
    path('unassign/<int:post_id>', UnassignTagsFromPostView.as_view(), name='tag-unassign'),  # POST /api/v1/tags/unassign/:post_id
    path('delete', TagDeleteView.as_view(), name='tag-delete'),  # DELETE /api/v1/tags/delete?tag_id=...
]
