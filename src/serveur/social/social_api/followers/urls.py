from django.urls import path
from .views import FollowersListView, FollowingListView, FollowUserView, UnfollowUserView

urlpatterns = [
    path('followers', FollowersListView.as_view(), name='followers-list'),  # GET /api/v1/followers
    path('following', FollowingListView.as_view(), name='following-list'),  # GET /api/v1/following
    path('follow/<int:id>', FollowUserView.as_view(), name='follow-user'),  # POST /api/v1/follow/:id
    path('unfollow/<int:id>', UnfollowUserView.as_view(), name='unfollow-user'),  # DELETE /api/v1/unfollow/:id
]
