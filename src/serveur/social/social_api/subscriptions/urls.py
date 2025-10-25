from django.urls import path
from .views import (
    SubscribeUserView,
    UnsubscribeUserView,
    SubscribeTopicView,
    UnsubscribeTopicView,
    SubscribeGroupView,
    UnsubscribeGroupView
)

urlpatterns = [
    path('users/<int:id>', SubscribeUserView.as_view(), name='subscribe-user'),  # POST /api/v1/subscriptions/users/:id
    path('users/<int:id>/unsubscribe', UnsubscribeUserView.as_view(), name='unsubscribe-user'),
    path('topics/<int:id>', SubscribeTopicView.as_view(), name='subscribe-topic'),
    path('topics/<int:id>/unsubscribe', UnsubscribeTopicView.as_view(), name='unsubscribe-topic'),
    path('groups/<int:id>', SubscribeGroupView.as_view(), name='subscribe-group'),
    path('groups/<int:id>/unsubscribe', UnsubscribeGroupView.as_view(), name='unsubscribe-group')
]
