from django.urls import path
from .views import (
    FollowersListView,
    FollowingListView,
    FollowUserView,
    UnfollowUserView,
    FollowerRequestsView,
    SendFollowerRequestView,
    AcceptFollowerRequestView,
    RefuseFollowerRequestView,
)

urlpatterns = [
    path('followers/me', FollowersListView.as_view(), name='followers-list'),  # GET /api/v1/followers/me
    path('following/me', FollowingListView.as_view(), name='following-list'),  # GET /api/v1/following/me
    path('following/<int:id>/unfollow', UnfollowUserView.as_view(), name='unfollow-user'),  # DELETE /api/v1/following/:id/unfollow
    path('followers/requests', FollowerRequestsView.as_view(), name='follower-requests'),  # GET /api/v1/followers/requests
    path('followers/<int:id>/request', SendFollowerRequestView.as_view(), name='follower-request-send'),  # POST /api/v1/followers/:id/request
    path('followers/<int:id>/accept', AcceptFollowerRequestView.as_view(), name='follower-request-accept'),  # POST /api/v1/followers/:id/accept
    path('followers/<int:id>/refuse', RefuseFollowerRequestView.as_view(), name='follower-request-refuse'),  # POST /api/v1/followers/:id/refuse
]
