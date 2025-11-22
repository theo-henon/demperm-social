"""URLs for Messaging app"""
from django.urls import path
from .views import (
    MessagesListView,
    ConversationDetailView,
    MessageCreateView,
    ConversationDeleteView,
    MessagesInboxView,
    MessageSendView
)

urlpatterns = [
    path('', MessagesListView.as_view(), name='messages-list'),
    path('inbox', MessagesInboxView.as_view(), name='messages-inbox'),
    path('send', MessageSendView.as_view(), name='message-send'),
    path('<str:id>', ConversationDetailView.as_view(), name='conversation-detail'),
    path('<str:user_id>/create', MessageCreateView.as_view(), name='message-create'),
    path('<str:id>/delete', ConversationDeleteView.as_view(), name='conversation-delete'),
]
