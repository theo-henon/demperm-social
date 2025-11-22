"""
Views for user blocking.
Based on specifications.md section 5.2.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction

from core.models import User, Block, Follower
from .serializers import BlockSerializer


class UserBlockView(APIView):
    """
    POST /users/{id}/block - Block a user.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        """Block a user."""
        # Get user to block by public_uuid
        blocked_user = get_object_or_404(User, public_uuid=user_id)
        
        # Cannot block yourself
        if blocked_user == request.user:
            return Response(
                {'error': 'You cannot block yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create block
                Block.objects.create(
                    blocker=request.user,
                    blocked=blocked_user
                )
                
                # Delete mutual follows if they exist
                Follower.objects.filter(
                    follower=request.user,
                    following=blocked_user
                ).delete()
                
                Follower.objects.filter(
                    follower=blocked_user,
                    following=request.user
                ).delete()
                
        except IntegrityError:
            # Already blocked
            return Response(
                {'error': 'You have already blocked this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': 'Utilisateur bloqué avec succès',
            'blocked_user_id': str(blocked_user.public_uuid)
        }, status=status.HTTP_201_CREATED)


class UserUnblockView(APIView):
    """
    DELETE /users/{id}/unblock - Unblock a user.
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, user_id):
        """Unblock a user."""
        # Get user to unblock by public_uuid
        blocked_user = get_object_or_404(User, public_uuid=user_id)
        
        # Try to delete the block
        deleted_count, _ = Block.objects.filter(
            blocker=request.user,
            blocked=blocked_user
        ).delete()
        
        if deleted_count == 0:
            return Response(
                {'error': 'This user is not blocked.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockedUsersListView(APIView):
    """
    GET /users/me/blocked - List blocked users.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of blocked users."""
        # Get all blocks by this user
        blocks = Block.objects.filter(blocker=request.user).select_related('blocked').order_by('-created_at')
        
        # Pagination
        page_num = request.query_params.get('page', 1)
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        paginator = Paginator(blocks, page_size)
        page = paginator.get_page(page_num)
        
        serializer = BlockSerializer(page.object_list, many=True)
        
        return Response({
            'blocked_users': serializer.data,
            'pagination': {
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': page_size
            }
        }, status=status.HTTP_200_OK)
