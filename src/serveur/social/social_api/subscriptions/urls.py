"""URLs for Subscriptions app"""
from django.urls import path
from .views import SubscribeForumView, UnsubscribeForumView, SubscribeSubforumView, UnsubscribeSubforumView

urlpatterns = [
    path('forums/<str:id>', SubscribeForumView.as_view(), name='subscribe-forum'),
    path('forums/<str:id>/unsubscribe', UnsubscribeForumView.as_view(), name='unsubscribe-forum'),
    path('subforums/<str:id>', SubscribeSubforumView.as_view(), name='subscribe-subforum'),
    path('subforums/<str:id>/unsubscribe', UnsubscribeSubforumView.as_view(), name='unsubscribe-subforum'),
]
