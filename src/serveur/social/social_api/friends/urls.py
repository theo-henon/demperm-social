from django.urls import path
from .views import (
    FriendsListView,
    FriendRequestsView,
    SendFriendRequestView,
    AcceptFriendRequestView,
    RefuseFriendRequestView,
    DeleteFriendView
)

urlpatterns = [
    path('', FriendsListView.as_view(), name='friends-list'),  # GET /api/v1/friends
    path('requests', FriendRequestsView.as_view(), name='friend-requests'),  # GET /api/v1/friends/requests
    path('<int:id>', SendFriendRequestView.as_view(), name='friend-request-send'),  # POST /api/v1/friends/:id
    path('<int:id>/accept', AcceptFriendRequestView.as_view(), name='friend-request-accept'),  # POST /api/v1/friends/:id/accept
    path('<int:id>/refuse', RefuseFriendRequestView.as_view(), name='friend-request-refuse'),  # POST /api/v1/friends/:id/refuse
    path('<int:id>/delete', DeleteFriendView.as_view(), name='friend-delete')  # DELETE /api/v1/friends/:id
]