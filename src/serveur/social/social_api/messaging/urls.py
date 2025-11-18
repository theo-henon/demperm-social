"""URLs for Messaging app"""
from django.urls import path
from .views import (
    MessagesListView,
    ConversationDetailView,
    MessageCreateView,
    ConversationDeleteView
)

urlpatterns = [
    path('', MessagesListView.as_view(), name='messages-list'),
    path('<str:id>', ConversationDetailView.as_view(), name='conversation-detail'),
    path('<str:user_id>/create', MessageCreateView.as_view(), name='message-create'),
    path('<str:id>/delete', ConversationDeleteView.as_view(), name='conversation-delete'),
]
