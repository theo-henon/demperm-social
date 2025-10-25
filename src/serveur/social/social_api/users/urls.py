from django.urls import path
from .views import UserMeView, UserDetailView, UserGroupsView

urlpatterns = [
    path('me', UserMeView.as_view(), name='user-me'),
    path('<int:id>', UserDetailView.as_view(), name='user-detail'),
    path('<int:id>/groups', UserGroupsView.as_view(), name='user-groups'),
]