from django.urls import path
from .views import SendMessageView, MessageThreadView

urlpatterns = [
    path('messages/<int:id>/send', SendMessageView.as_view(), name='send-message'),  # POST /api/v1/messages/:id/send
    path('messages/<int:id>', MessageThreadView.as_view(), name='message-thread'),  # GET /api/v1/messages/:id
]
