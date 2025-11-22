"""
Views for comments on posts.
Based on specifications.md section 5.7.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator

from api.db.models import Post, Comment, User
from .serializers import CommentSerializer, CommentCreateSerializer, CommentReplySerializer


class PostCommentsListView(APIView):
    """
    GET /posts/{id}/comments - List comments for a post.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """Get all comments for a specific post."""
        # Get post by public_uuid
        post = get_object_or_404(Post, public_uuid=post_id, deleted_at__isnull=True)
        
        # Check if user has access to post (visibility rules)
        # TODO: Add proper visibility checks based on post.visibility and followers
        
        # Get only top-level comments (no parent)
        comments = Comment.objects.filter(
            post=post,
            parent_comment__isnull=True,
            deleted_at__isnull=True
        ).select_related('author').order_by('-created_at')
        
        # Pagination
        page_num = request.query_params.get('page', 1)
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        paginator = Paginator(comments, page_size)
        page = paginator.get_page(page_num)
        
        serializer = CommentSerializer(page.object_list, many=True)
        
        return Response({
            'comments': serializer.data,
            'pagination': {
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': page_size
            }
        }, status=status.HTTP_200_OK)


class PostCommentCreateView(APIView):
    """
    POST /posts/{id}/comments/create - Create a comment on a post.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Create a new comment on a post."""
        # Get post by public_uuid
        post = get_object_or_404(Post, public_uuid=post_id, deleted_at__isnull=True)
        
        # Validate request data
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Check if post author blocked the commenting user
        # TODO: Check post visibility
        
        # Create comment
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=serializer.validated_data['content']
        )
        
        # Serialize and return
        response_serializer = CommentSerializer(comment)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(APIView):
    """
    DELETE /comments/{id}/delete - Delete own comment.
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, comment_id):
        """Soft delete a comment."""
        # Get comment by public_uuid
        comment = get_object_or_404(Comment, public_uuid=comment_id, deleted_at__isnull=True)
        
        # Check ownership
        if comment.author != request.user:
            return Response(
                {'error': 'You can only delete your own comments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete
        comment.deleted_at = timezone.now()
        comment.deleted_by = request.user
        comment.save()
        
        # Also soft delete all replies (CASCADE)
        comment.replies.filter(deleted_at__isnull=True).update(
            deleted_at=timezone.now(),
            deleted_by=request.user
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentRepliesListView(APIView):
    """
    GET /comments/{id}/replies - Get replies to a comment.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, comment_id):
        """Get all replies to a specific comment."""
        # Get parent comment by public_uuid
        parent_comment = get_object_or_404(Comment, public_uuid=comment_id, deleted_at__isnull=True)
        
        # Get replies
        replies = Comment.objects.filter(
            parent_comment=parent_comment,
            deleted_at__isnull=True
        ).select_related('author').order_by('created_at')
        
        # Pagination
        page_num = request.query_params.get('page', 1)
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        paginator = Paginator(replies, page_size)
        page = paginator.get_page(page_num)
        
        serializer = CommentSerializer(page.object_list, many=True)
        
        return Response({
            'replies': serializer.data,
            'pagination': {
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': page_size
            }
        }, status=status.HTTP_200_OK)


class CommentReplyView(APIView):
    """
    POST /comments/{id}/reply - Reply to a comment.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, comment_id):
        """Create a reply to a comment."""
        # Get parent comment by public_uuid
        parent_comment = get_object_or_404(Comment, public_uuid=comment_id, deleted_at__isnull=True)
        
        # Validate request data
        serializer = CommentReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Check if post author or comment author blocked the replying user
        
        # Create reply
        reply = Comment.objects.create(
            post=parent_comment.post,
            author=request.user,
            content=serializer.validated_data['content'],
            parent_comment=parent_comment
        )
        
        # Serialize and return
        response_serializer = CommentSerializer(reply)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
