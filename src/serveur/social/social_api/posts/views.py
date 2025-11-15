"""
Views pour l'app posts
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Post, User, AuditLog
from core.permissions import IsOwner, PrivacyGuard
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer, PostFeedSerializer
)


class PostCreateView(APIView):
    """Créer un nouveau post"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer un post",
        tags=["Posts"],
        request_body=PostCreateSerializer,
        responses={
            201: PostSerializer,
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            
            # Log (commented out temporarily)
            # AuditLog.objects.create(
            #     user=request.user,
            #     action='create_post',
            #     details={'post_id': str(post.public_uuid)}
            # )
            
            response_serializer = PostSerializer(post, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """Récupérer les détails d'un post"""
    permission_classes = [IsAuthenticated, PrivacyGuard]
    
    @swagger_auto_schema(
        operation_description="Détails d'un post",
        tags=["Posts"],
        responses={
            200: PostSerializer,
            404: openapi.Response(description="Post non trouvé"),
            401: openapi.Response(description="Non authentifié"),
            403: openapi.Response(description="Accès refusé")
        }
    )
    def get(self, request, id):
        post = get_object_or_404(Post, public_uuid=id, deleted_at__isnull=True)
        
        # Vérifier les permissions de visibilité
        self.check_object_permissions(request, post)
        
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostUpdateView(APIView):
    """Mettre à jour un post existant"""
    permission_classes = [IsAuthenticated, IsOwner]
    
    @swagger_auto_schema(
        operation_description="Mettre à jour un post",
        tags=["Posts"],
        request_body=PostUpdateSerializer,
        responses={
            200: PostSerializer,
            400: openapi.Response(description="Données invalides"),
            403: openapi.Response(description="Accès interdit"),
            404: openapi.Response(description="Post non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def patch(self, request, id):
        post = get_object_or_404(Post, public_uuid=id, deleted_at__isnull=True)
        
        # Vérifier que l'utilisateur est le propriétaire
        self.check_object_permissions(request, post)
        
        serializer = PostUpdateSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            post = serializer.save(edited=True)
            
            # Log
            AuditLog.objects.create(
                user=request.user,
                action='update_post',
                details={'post_id': str(post.public_uuid)}
            )
            
            response_serializer = PostSerializer(post, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDeleteView(APIView):
    """Supprimer (soft delete) un post"""
    permission_classes = [IsAuthenticated, IsOwner]
    
    @swagger_auto_schema(
        operation_description="Supprimer un post",
        tags=["Posts"],
        responses={
            204: openapi.Response(description="Post supprimé"),
            403: openapi.Response(description="Accès interdit"),
            404: openapi.Response(description="Post non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def delete(self, request, id):
        post = get_object_or_404(Post, public_uuid=id, deleted_at__isnull=True)
        
        # Vérifier que l'utilisateur est le propriétaire
        self.check_object_permissions(request, post)
        
        # Soft delete
        from django.utils import timezone
        post.deleted_at = timezone.now()
        post.save()
        
        # Log
        AuditLog.objects.create(
            user=request.user,
            action='delete_post',
            details={'post_id': str(post.public_uuid)}
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostFeedView(APIView):
    """Récupérer le feed personnalisé (posts des personnes suivies)"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupère le fil d'actualité (feed) des posts",
        tags=["Posts"],
        responses={
            200: PostFeedSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Récupérer les utilisateurs suivis
        following_ids = request.user.following.values_list('following_id', flat=True)
        
        # Posts de l'utilisateur + posts des personnes suivies
        # avec visibilité appropriée
        posts = Post.objects.filter(
            Q(author=request.user) |  # Posts de l'utilisateur
            Q(author_id__in=following_ids, visibility__in=['public', 'followers']) |  # Posts des suivis
            Q(visibility='public')  # Posts publics
        ).filter(
            deleted_at__isnull=True
        ).select_related('author').order_by('-created_at')[:50]
        
        serializer = PostFeedSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostDiscoverView(APIView):
    """Découvrir de nouveaux posts publics (exploration)"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Découvrir des posts (découverte)",
        tags=["Posts"],
        responses={
            200: PostFeedSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Posts publics de personnes non suivies
        following_ids = request.user.following.values_list('following_id', flat=True)
        
        posts = Post.objects.filter(
            visibility='public',
            deleted_at__isnull=True
        ).exclude(
            author=request.user
        ).exclude(
            author_id__in=following_ids
        ).select_related('author').order_by('-likes', '-created_at')[:50]
        
        serializer = PostFeedSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
