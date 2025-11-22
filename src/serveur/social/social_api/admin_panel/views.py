"""
Views for admin panel.
Specifications.md section 5.13 - All endpoints require is_admin = TRUE.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta

from core.models import Report, User, Post, Comment, AuditLog, Like, Conversation, Forum, Tag
from .permissions import IsAdmin
from .serializers import (
    AdminReportListSerializer, AdminReportResolveSerializer,
    AdminUserBanSerializer, AdminStatsUsersSerializer,
    AdminStatsPostsSerializer, AdminStatsActivitySerializer
)


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


class AdminReportsListView(APIView):
    """
    GET /admin/reports - List all reports with filters.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """List reports with optional status filter."""
        # Get query params
        status_filter = request.GET.get('status', None)
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # Build query
        reports = Report.objects.all().select_related('reporter').order_by('-created_at')
        
        if status_filter:
            reports = reports.filter(status=status_filter)
        
        # Pagination
        total_items = reports.count()
        total_pages = (total_items + page_size - 1) // page_size
        offset = (page - 1) * page_size
        paginated_reports = reports[offset:offset + page_size]
        
        # Serialize
        serializer = AdminReportListSerializer(paginated_reports, many=True)
        
        return Response({
            'reports': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'total_items': total_items,
                'has_next': page < total_pages,
                'has_previous': page > 1
            }
        }, status=status.HTTP_200_OK)


class AdminReportResolveView(APIView):
    """
    POST /admin/reports/{id}/resolve - Mark report as resolved.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, report_id):
        """Resolve a report."""
        try:
            report = Report.objects.get(public_uuid=report_id)
        except Report.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if report.status != 'pending':
            return Response(
                {'detail': f'Report already {report.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AdminReportResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update report
        report.status = 'resolved'
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.save()
        
        # Log action
        AuditLog.objects.create(
            actor=request.user,
            event_type='report_resolved',
            target_type='report',
            target_id=str(report.public_uuid),
            payload={
                'action_taken': serializer.validated_data['action_taken'],
                'notes': serializer.validated_data.get('notes', '')
            }
        )
        
        return Response({
            'message': 'Report resolved successfully',
            'report_id': str(report.public_uuid),
            'status': 'resolved'
        }, status=status.HTTP_200_OK)


class AdminReportRejectView(APIView):
    """
    POST /admin/reports/{id}/reject - Reject a report.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, report_id):
        """Reject a report."""
        try:
            report = Report.objects.get(public_uuid=report_id)
        except Report.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if report.status != 'pending':
            return Response(
                {'detail': f'Report already {report.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update report
        report.status = 'rejected'
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.save()
        
        # Log action
        AuditLog.objects.create(
            actor=request.user,
            event_type='report_rejected',
            target_type='report',
            target_id=str(report.public_uuid),
            payload={'reason': request.data.get('reason', 'No reason provided')}
        )
        
        return Response({
            'message': 'Report rejected',
            'report_id': str(report.public_uuid),
            'status': 'rejected'
        }, status=status.HTTP_200_OK)


class AdminUserBanView(APIView):
    """
    POST /admin/users/{id}/ban - Ban a user.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, user_id):
        """Ban a user."""
        try:
            user = User.objects.get(public_uuid=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_banned:
            return Response(
                {'detail': 'User already banned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AdminUserBanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Ban user
        user.is_banned = True
        user.banned_at = timezone.now()
        user.ban_reason = serializer.validated_data['reason']
        user.save()
        
        # TODO: Invalidate all refresh tokens in Redis
        # from django.core.cache import cache
        # cache.delete_pattern(f'refresh_token:{user.id}:*')
        
        # Log action
        AuditLog.objects.create(
            actor=request.user,
            event_type='user_banned',
            target_type='user',
            target_id=str(user.public_uuid),
            payload={
                'reason': serializer.validated_data['reason'],
                'duration_days': serializer.validated_data.get('duration_days')
            }
        )
        
        return Response({
            'message': f'User {user.username} has been banned',
            'user_id': str(user.public_uuid),
            'banned_at': user.banned_at
        }, status=status.HTTP_200_OK)


class AdminUserUnbanView(APIView):
    """
    POST /admin/users/{id}/unban - Unban a user.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, user_id):
        """Unban a user."""
        try:
            user = User.objects.get(public_uuid=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.is_banned:
            return Response(
                {'detail': 'User is not banned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Unban user
        user.is_banned = False
        user.banned_at = None
        user.ban_reason = None
        user.save()
        
        # Log action
        AuditLog.objects.create(
            actor=request.user,
            event_type='user_unbanned',
            target_type='user',
            target_id=str(user.public_uuid),
            payload={'unbanned_by': request.user.username}
        )
        
        return Response({
            'message': f'User {user.username} has been unbanned',
            'user_id': str(user.public_uuid)
        }, status=status.HTTP_200_OK)


class AdminPostRemoveView(APIView):
    """
    DELETE /admin/posts/{id}/remove - Remove a post (moderation).
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def delete(self, request, post_id):
        """Soft delete a post."""
        try:
            post = Post.objects.get(public_uuid=post_id, deleted_at__isnull=True)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Soft delete
        post.deleted_at = timezone.now()
        post.save()
        
        # Log action
        AuditLog.objects.create(
            actor=request.user,
            event_type='post_removed',
            target_type='post',
            target_id=str(post.public_uuid),
            payload={
                'reason': request.data.get('reason', 'Moderation'),
                'original_author': post.author.username
            }
        )
        
        return Response({
            'message': 'Post removed successfully',
            'post_id': str(post.public_uuid)
        }, status=status.HTTP_200_OK)


class AdminCommentRemoveView(APIView):
    """
    DELETE /admin/comments/{id}/remove - Remove a comment (moderation).
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def delete(self, request, comment_id):
        """Soft delete a comment."""
        try:
            comment = Comment.objects.get(public_uuid=comment_id, deleted_at__isnull=True)
        except Comment.DoesNotExist:
            return Response({'detail': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Soft delete
        comment.deleted_at = timezone.now()
        comment.save()
        
        # Log action
        AuditLog.objects.create(
            actor=request.user,
            event_type='comment_removed',
            target_type='comment',
            target_id=str(comment.public_uuid),
            payload={
                'reason': request.data.get('reason', 'Moderation'),
                'original_author': comment.author.username
            }
        )
        
        return Response({
            'message': 'Comment removed successfully',
            'comment_id': str(comment.public_uuid)
        }, status=status.HTTP_200_OK)


class AdminStatsUsersView(APIView):
    """
    GET /admin/stats/users - Get user statistics.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Get user statistics."""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        
        stats = {
            'total_users': User.objects.count(),
            'new_users_today': User.objects.filter(created_at__gte=today_start).count(),
            'new_users_this_week': User.objects.filter(created_at__gte=week_start).count(),
            'active_users_today': User.objects.filter(last_login__gte=today_start).count(),
            'banned_users': User.objects.filter(is_banned=True).count()
        }
        
        serializer = AdminStatsUsersSerializer(data=stats)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminStatsPostsView(APIView):
    """
    GET /admin/stats/posts - Get post statistics.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Get post statistics."""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        
        stats = {
            'total_posts': Post.objects.filter(deleted_at__isnull=True).count(),
            'posts_today': Post.objects.filter(created_at__gte=today_start, deleted_at__isnull=True).count(),
            'posts_this_week': Post.objects.filter(created_at__gte=week_start, deleted_at__isnull=True).count(),
            'deleted_posts': Post.objects.filter(deleted_at__isnull=False).count()
        }
        
        serializer = AdminStatsPostsSerializer(data=stats)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminStatsActivityView(APIView):
    """
    GET /admin/stats/activity - Get activity statistics.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        """Get activity statistics."""
        stats = {
            'total_comments': Comment.objects.filter(deleted_at__isnull=True).count(),
            'total_likes': Like.objects.count(),
            'total_reports': Report.objects.count(),
            'pending_reports': Report.objects.filter(status='pending').count(),
            'active_conversations': Conversation.objects.count()
        }
        
        serializer = AdminStatsActivitySerializer(data=stats)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminDomainCreateView(APIView):
    """POST /admin/domains/create - Create new domain (top-level forum)."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        """Create a new domain (Forum with parent_forum=None)."""
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        
        if not name or len(name) < 2 or len(name) > 100:
            return Response(
                {'error': 'Name must be between 2 and 100 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Forum.objects.filter(name__iexact=name, parent_forum__isnull=True).exists():
            return Response(
                {'error': 'A domain with this name already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        domain = Forum.objects.create(
            name=name,
            description=description or None,
            parent_forum=None,
            visibility='public'
        )
        
        AuditLog.objects.create(
            actor=request.user,
            event_type='admin.domain.create',
            payload={'domain_id': str(domain.public_uuid), 'name': name},
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'domain_id': str(domain.public_uuid),
            'name': domain.name,
            'description': domain.description,
            'created_at': domain.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class AdminDomainUpdateView(APIView):
    """PATCH /admin/domains/{id} - Update domain."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def patch(self, request, id):
        """Update domain (top-level forum) details."""
        try:
            domain = Forum.objects.get(public_uuid=id, parent_forum__isnull=True)
        except Forum.DoesNotExist:
            return Response({'error': 'Domain not found'}, status=status.HTTP_404_NOT_FOUND)
        
        name = request.data.get('name')
        description = request.data.get('description')
        
        if name is not None:
            name = name.strip()
            if not name or len(name) < 2 or len(name) > 100:
                return Response(
                    {'error': 'Name must be between 2 and 100 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check name uniqueness
            if Forum.objects.filter(name__iexact=name, parent_forum__isnull=True).exclude(id=domain.id).exists():
                return Response(
                    {'error': 'A domain with this name already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            domain.name = name
        
        if description is not None:
            domain.description = description.strip() or None
        
        domain.save()
        
        AuditLog.objects.create(
            actor=request.user,
            event_type='admin.domain.update',
            payload={'domain_id': str(domain.public_uuid), 'changes': request.data},
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'domain_id': str(domain.public_uuid),
            'name': domain.name,
            'description': domain.description
        })


class AdminDomainDeleteView(APIView):
    """DELETE /admin/domains/{id} - Delete domain (cascade to subforums)."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def delete(self, request, id):
        """Delete a domain (top-level forum) and all its subforums."""
        try:
            domain = Forum.objects.get(public_uuid=id, parent_forum__isnull=True)
        except Forum.DoesNotExist:
            return Response({'error': 'Domain not found'}, status=status.HTTP_404_NOT_FOUND)
        
        domain_name = domain.name
        
        # Log before deletion
        AuditLog.objects.create(
            actor=request.user,
            event_type='admin.domain.delete',
            payload={'domain_id': str(domain.public_uuid), 'name': domain_name},
            ip_address=get_client_ip(request)
        )
        
        domain.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminTagDeleteView(APIView):
    """DELETE /admin/tags/delete?tag_id=uuid - Delete tag."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def delete(self, request):
        """Delete a tag."""
        tag_id = request.GET.get('tag_id')
        
        if not tag_id:
            return Response(
                {'error': 'tag_id query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tag = Tag.objects.get(public_uuid=tag_id)
        except Tag.DoesNotExist:
            return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
        
        tag_name = tag.name
        
        # Log before deletion
        AuditLog.objects.create(
            actor=request.user,
            event_type='admin.tag.delete',
            payload={'tag_id': str(tag.public_uuid), 'name': tag_name},
            ip_address=get_client_ip(request)
        )
        
        tag.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
