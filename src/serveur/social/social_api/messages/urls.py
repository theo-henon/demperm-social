from django.urls import path
from .views import ConversationView, ConversationsListView, CreateConversationView, DeleteConversationView

urlpatterns = [
    path('messages/', ConversationsListView.as_view(), name='conversations-list'),  # GET /api/v1/messages/conversations
    path('messages/<int:id>', ConversationView.as_view(), name='conversation-view'),  # GET /api/v1/messages/:id
    path('messages/<int:user_id>/create', CreateConversationView.as_view(), name='create-conversation'),  # POST /api/v1/messages/conversations/:id/create
    path('messages/<int:id>/delete', DeleteConversationView.as_view(), name='delete-conversation'),  # DELETE /api/v1/messages/:id/delete
]
