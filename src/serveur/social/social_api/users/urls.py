from django.urls import path
from .views import UserMeView, UserDetailView, UserSearchView, UserDiscoverView, UserSettingsView, UserBulkView

urlpatterns = [
    path('me', UserMeView.as_view(), name='user-me'),
    path('me/settings', UserSettingsView.as_view(), name='user-settings'),
    path('search', UserSearchView.as_view(), name='user-search'),
    path('bulk', UserBulkView.as_view(), name='user-bulk'),
    path('discover', UserDiscoverView.as_view(), name='user-discover'),
    path('<uuid:id>', UserDetailView.as_view(), name='user-detail'),
]
