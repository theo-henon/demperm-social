"""
Views for content reports.
Based on specifications.md section 5.12.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from api.db.models import Report, Post, Comment, User
from .serializers import ReportCreateSerializer, ReportSerializer


class ReportCreateView(APIView):
    """
    POST /reports/create - Create a content report.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a report."""
        # Validate request data
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_type = serializer.validated_data['target_type']
        target_id = serializer.validated_data['target_id']
        reason = serializer.validated_data['reason']
        description = serializer.validated_data.get('description', '')
        
        # Verify target exists
        try:
            if target_type == 'post':
                target = Post.objects.get(public_uuid=target_id, deleted_at__isnull=True)
            elif target_type == 'comment':
                target = Comment.objects.get(public_uuid=target_id, deleted_at__isnull=True)
            elif target_type == 'user':
                target = User.objects.get(public_uuid=target_id)
        except (Post.DoesNotExist, Comment.DoesNotExist, User.DoesNotExist):
            return Response(
                {'detail': f'{target_type.capitalize()} not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create report
        report = Report.objects.create(
            reporter=request.user,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            description=description,
            status='pending'
        )
        
        # TODO: Log in AuditLogs
        # TODO: Notify admins if threshold reached
        
        response_serializer = ReportSerializer(report)
        
        return Response({
            'report_id': str(report.public_uuid),
            'message': 'Signalement enregistré, il sera traité par un modérateur',
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
