from django.urls import path
from .views import (
    FollowersListView,
    FollowingListView,
    FollowUserView,
    UnfollowUserView,
    FollowerRequestsView,
    AcceptFollowerRequestView,
    RefuseFollowerRequestView,
)

urlpatterns = [
    path('followers/me', FollowersListView.as_view(), name='followers-list'),  # GET /api/v1/followers/me
    path('following/me', FollowingListView.as_view(), name='following-list'),  # GET /api/v1/following/me
    path('followers/<uuid:id>/follow', FollowUserView.as_view(), name='follow-user'),  # POST /api/v1/followers/:id/follow
    path('followers/<uuid:id>/unfollow', UnfollowUserView.as_view(), name='unfollow-user'),  # DELETE /api/v1/followers/:id/unfollow
    path('followers/requests', FollowerRequestsView.as_view(), name='follower-requests'),  # GET /api/v1/followers/requests
    path('followers/requests/<uuid:id>/accept', AcceptFollowerRequestView.as_view(), name='follower-request-accept'),  # POST /api/v1/followers/requests/:id/accept
    path('followers/requests/<uuid:id>/refuse', RefuseFollowerRequestView.as_view(), name='follower-request-refuse'),  # POST /api/v1/followers/requests/:id/refuse
]
