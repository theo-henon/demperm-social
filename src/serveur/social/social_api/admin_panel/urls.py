"""
URL patterns for admin panel.
Specifications.md section 5.13 - All endpoints require is_admin = TRUE.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Reports Management
    path('admin/reports', views.AdminReportsListView.as_view(), name='admin-reports-list'),
    path('admin/reports/<uuid:report_id>/resolve', views.AdminReportResolveView.as_view(), name='admin-report-resolve'),
    path('admin/reports/<uuid:report_id>/reject', views.AdminReportRejectView.as_view(), name='admin-report-reject'),
    
    # User Management
    path('admin/users/<uuid:user_id>/ban', views.AdminUserBanView.as_view(), name='admin-user-ban'),
    path('admin/users/<uuid:user_id>/unban', views.AdminUserUnbanView.as_view(), name='admin-user-unban'),
    
    # Content Moderation
    path('admin/posts/<uuid:post_id>/remove', views.AdminPostRemoveView.as_view(), name='admin-post-remove'),
    path('admin/comments/<uuid:comment_id>/remove', views.AdminCommentRemoveView.as_view(), name='admin-comment-remove'),
    
    # Domains Management
    path('admin/domains/create', views.AdminDomainCreateView.as_view(), name='admin-domain-create'),
    path('admin/domains/<uuid:id>', views.AdminDomainUpdateView.as_view(), name='admin-domain-update'),
    path('admin/domains/<uuid:id>/delete', views.AdminDomainDeleteView.as_view(), name='admin-domain-delete'),
    
    # Tags Management
    path('admin/tags/delete', views.AdminTagDeleteView.as_view(), name='admin-tag-delete'),
    
    # Statistics
    path('admin/stats/users', views.AdminStatsUsersView.as_view(), name='admin-stats-users'),
    path('admin/stats/posts', views.AdminStatsPostsView.as_view(), name='admin-stats-posts'),
    path('admin/stats/activity', views.AdminStatsActivityView.as_view(), name='admin-stats-activity'),
]
