from django.urls import path
from .views import (
    SubscribeForumView,
    UnsubscribeForumView,
    SubscribeSubforumView,
    UnsubscribeSubforumView
)

urlpatterns = [
    path('forums/<int:id>', SubscribeForumView.as_view(), name='subscribe-forum'),  # POST /api/v1/subscriptions/forums/:id
    path('forums/<int:id>/unsubscribe', UnsubscribeForumView.as_view(), name='unsubscribe-forum'),  # DELETE /api/v1/subscriptions/forums/:id/unsubscribe
    path('subforums/<int:id>', SubscribeSubforumView.as_view(), name='subscribe-subforum'),  # POST /api/v1/subscriptions/subforums/:id
    path('subforums/<int:id>/unsubscribe', UnsubscribeSubforumView.as_view(), name='unsubscribe-subforum'),  # DELETE /api/v1/subscriptions/subforums/:id/unsubscribe
]
