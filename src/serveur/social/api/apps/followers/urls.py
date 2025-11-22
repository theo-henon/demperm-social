"""URLs for Followers app"""
from django.urls import path
from .views import (
    FollowersMeView,
    FollowingMeView,
    FollowerRequestsView,
    FollowerRequestView,
    FollowerAcceptView,
    FollowerRefuseView,
    UnfollowView
)

urlpatterns = [
    path('followers/me', FollowersMeView.as_view(), name='followers-me'),
    path('following/me', FollowingMeView.as_view(), name='following-me'),
    path('followers/requests', FollowerRequestsView.as_view(), name='follower-requests'),
    path('followers/<str:id>/request', FollowerRequestView.as_view(), name='follower-request'),
    path('followers/<str:id>/accept', FollowerAcceptView.as_view(), name='follower-accept'),
    path('followers/<str:id>/refuse', FollowerRefuseView.as_view(), name='follower-refuse'),
    path('following/<str:id>/unfollow', UnfollowView.as_view(), name='unfollow'),
]
