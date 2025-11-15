from django.urls import path
from .views import SubscribeForumView, UnsubscribeForumView, MySubscriptionsView

urlpatterns = [
    path('me', MySubscriptionsView.as_view(), name='subscriptions-me'),  # GET /api/v1/subscriptions/me
    path('forums/<uuid:uuid>', SubscribeForumView.as_view(), name='subscribe-forum'),  # POST /api/v1/subscriptions/forums/:uuid
    path('forums/<uuid:uuid>/unsubscribe', UnsubscribeForumView.as_view(), name='unsubscribe-forum'),  # DELETE /api/v1/subscriptions/forums/:uuid/unsubscribe
]
