from django.urls import path
from .views import DomainListView, DomainDetailView, DomainSubforumsView, DomainSubforumCreateView

urlpatterns = [
    path('', DomainListView.as_view(), name='domain-list'),  # GET /api/v1/domains
    path('<int:id>', DomainDetailView.as_view(), name='domain-detail'),  # GET /api/v1/domains/:id
    path('<int:id>/subforums', DomainSubforumsView.as_view(), name='domain-subforums'),  # GET /api/v1/domains/:id/subforums
    path('<int:id>/subforums/create', DomainSubforumCreateView.as_view(), name='domain-subforum-create'),  # POST /api/v1/domains/:id/subforums/create
]
