"""Messaging URLs"""
from django.urls import path
from .views import ConversationsView, ConversationDetailView, MessageCreateView, ConversationDeleteView

urlpatterns = [
    path('', ConversationsView.as_view(), name='conversations'),
    path('<uuid:uuid>', ConversationDetailView.as_view(), name='conversation-detail'),
    path('<uuid:uuid>/create', MessageCreateView.as_view(), name='message-create'),
    path('<uuid:uuid>/delete', ConversationDeleteView.as_view(), name='conversation-delete'),
]
