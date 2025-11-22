"""
Views for likes on posts.
Based on specifications.md section 5.6.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction

from core.models import Post, Like
from .serializers import LikeSerializer


class PostLikeView(APIView):
    """
    POST /posts/{id}/like - Like a post.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Like a post."""
        # Get post by public_uuid
        post = get_object_or_404(Post, public_uuid=post_id, deleted_at__isnull=True)
        
        # TODO: Check if post author blocked the user
        # TODO: Check post visibility
        
        try:
            with transaction.atomic():
                # Create like (UNIQUE constraint prevents duplicates)
                Like.objects.create(
                    user=request.user,
                    post=post
                )
                
                # Increment like_count (if field exists)
                # Note: Post model doesn't have like_count field yet
                # We'll count dynamically for now
                
        except IntegrityError:
            # Like already exists
            return Response(
                {'error': 'You have already liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Count total likes
        like_count = post.likes.count()
        
        return Response({
            'message': 'Post liké',
            'like_count': like_count
        }, status=status.HTTP_201_CREATED)


class PostUnlikeView(APIView):
    """
    DELETE /posts/{id}/unlike - Remove like from a post.
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, post_id):
        """Unlike a post."""
        # Get post by public_uuid
        post = get_object_or_404(Post, public_uuid=post_id, deleted_at__isnull=True)
        
        # Try to delete the like
        deleted_count, _ = Like.objects.filter(
            user=request.user,
            post=post
        ).delete()
        
        if deleted_count == 0:
            return Response(
                {'error': 'You have not liked this post.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostLikesListView(APIView):
    """
    GET /posts/{id}/likes - List users who liked a post.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """Get list of users who liked a post."""
        # Get post by public_uuid
        post = get_object_or_404(Post, public_uuid=post_id, deleted_at__isnull=True)
        
        # TODO: Check post visibility
        
        # Get likes with user info
        likes = Like.objects.filter(post=post).select_related('user').order_by('-created_at')
        
        # Pagination
        page_num = request.query_params.get('page', 1)
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        paginator = Paginator(likes, page_size)
        page = paginator.get_page(page_num)
        
        serializer = LikeSerializer(page.object_list, many=True)
        
        return Response({
            'likes': serializer.data,
            'pagination': {
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': page_size
            },
            'total_likes': paginator.count
        }, status=status.HTTP_200_OK)
