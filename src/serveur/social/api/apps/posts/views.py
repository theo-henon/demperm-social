"""
Posts API views.
Based on Specifications.md section 4.3.
"""
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.db.models import Post, User, Follower, ForumSubscription, AuditLog
from api.db.serializers import PostSerializer, PostListSerializer
from api.common.permissions import IsOwnerOrModerator, PrivacyGuard


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


class PostCreateView(APIView):
    """POST /api/v1/posts/create"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer un post",
        tags=["Posts"],
        request_body=PostSerializer,
        responses={
            201: openapi.Response(description="Post créé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            
            AuditLog.objects.create(
                event_type='post.created',
                actor=request.user,
                target_type='post',
                target_id=post.id,
                ip_address=get_client_ip(request)
            )
            
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """GET /api/v1/posts/{id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Détails d'un post",
        tags=["Posts"],
        responses={
            200: openapi.Response(description="Post trouvé"),
            401: openapi.Response(description="Non authentifié"),
            403: openapi.Response(description="Accès interdit"),
            404: openapi.Response(description="Post non trouvé")
        }
    )
    def get(self, request, id):
        post = Post.objects.filter(public_uuid=id, deleted_at__isnull=True).first()
        
        if not post:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check privacy
        privacy_guard = PrivacyGuard()
        if not privacy_guard.has_object_permission(request, self, post):
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PostSerializer(post)
        return Response(serializer.data)


class PostDeleteView(APIView):
    """DELETE /api/v1/posts/{id}/delete"""
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    
    @swagger_auto_schema(
        operation_description="Supprimer un post",
        tags=["Posts"],
        responses={
            204: openapi.Response(description="Post supprimé"),
            401: openapi.Response(description="Non authentifié"),
            403: openapi.Response(description="Accès interdit"),
            404: openapi.Response(description="Post non trouvé")
        }
    )
    def delete(self, request, id):
        from django.utils import timezone
        
        post = Post.objects.filter(public_uuid=id, deleted_at__isnull=True).first()
        
        if not post:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        is_owner_or_mod = IsOwnerOrModerator()
        if not is_owner_or_mod.has_object_permission(request, self, post):
            return Response(
                {'error': 'Action non autorisée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete
        post.deleted_at = timezone.now()
        post.deleted_by = request.user
        post.save()
        
        AuditLog.objects.create(
            event_type='post.deleted',
            actor=request.user,
            target_type='post',
            target_id=post.id,
            ip_address=get_client_ip(request),
            payload={'reason': request.data.get('reason', '')}
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostFeedView(APIView):
    """GET /api/v1/posts/feed"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupère le fil d'actualité (feed) des posts",
        tags=["Posts"],
        responses={
            200: openapi.Response(description="Feed récupéré"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Get users I'm following
        following_ids = Follower.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        
        # Get forums I'm subscribed to
        subscribed_forum_ids = ForumSubscription.objects.filter(
            user=request.user
        ).values_list('forum_id', flat=True)
        
        # Build query
        posts = Post.objects.filter(
            deleted_at__isnull=True
        ).filter(
            Q(author_id__in=following_ids, visibility__in=['followers', 'public']) |
            Q(subforum_id__in=subscribed_forum_ids)
        ).select_related('author').prefetch_related('tags').order_by('-created_at')[:20]
        
        serializer = PostListSerializer(posts, many=True)
        return Response({
            'posts': serializer.data,
            'next_cursor': None
        })


class PostDiscoverView(APIView):
    """GET /api/v1/posts/discover"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Découvrir des posts (découverte)",
        tags=["Posts"],
        responses={
            200: openapi.Response(description="Posts découverts"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Discover public posts (trending/recent)
        posts = Post.objects.filter(
            visibility='public',
            deleted_at__isnull=True
        ).select_related('author').prefetch_related('tags').order_by('-created_at')[:20]
        
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
