"""
Views pour l'app tags
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Tag, Post
from .serializers import TagSerializer, TagCreateSerializer, PostTagsSerializer


class TagCreateView(APIView):
    """Créer un nouveau tag"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Crée un nouveau tag",
        tags=["Tags"],
        request_body=TagCreateSerializer,
        responses={
            201: TagSerializer,
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        serializer = TagCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tag = Tag.objects.create(
            name=serializer.validated_data['name']
        )
        
        response_serializer = TagSerializer(tag)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TagListView(APIView):
    """Liste tous les tags disponibles"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste tous les tags disponibles",
        tags=["Tags"],
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Recherche de tags par nom",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: TagSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        search = request.GET.get('search', '').strip()
        
        if search:
            tags = Tag.objects.filter(name__icontains=search).order_by('name')[:20]
        else:
            tags = Tag.objects.all().order_by('name')[:50]
        
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignTagsToPostView(APIView):
    """Assigner des tags à un post"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Assigner des tags à un post",
        tags=["Tags"],
        request_body=PostTagsSerializer,
        responses={
            200: openapi.Response(description="Tags assignés au post"),
            400: openapi.Response(description="Requête invalide"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Post ou tag non trouvé")
        }
    )
    def post(self, request, post_id):
        post = get_object_or_404(Post, public_uuid=post_id)
        
        # Vérifier que l'utilisateur est le propriétaire du post
        if post.author != request.user:
            return Response(
                {"error": "Vous ne pouvez pas modifier les tags de ce post"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PostTagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Récupérer les tags
        tag_uuids = serializer.validated_data['tags']
        tags = Tag.objects.filter(public_uuid__in=tag_uuids)
        
        if tags.count() != len(tag_uuids):
            return Response(
                {"error": "Un ou plusieurs tags n'existent pas"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Ajouter les tags au post
        post.tags.add(*tags)
        
        # Retourner les tags actuels du post
        current_tags = TagSerializer(post.tags.all(), many=True)
        return Response({
            "post_id": str(post.public_uuid),
            "tags": current_tags.data
        }, status=status.HTTP_200_OK)


class UnassignTagsFromPostView(APIView):
    """Désassigner des tags d'un post"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Désassigner des tags d'un post",
        tags=["Tags"],
        request_body=PostTagsSerializer,
        responses={
            200: openapi.Response(description="Tags désassignés du post"),
            400: openapi.Response(description="Requête invalide"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Post ou tag non trouvé")
        }
    )
    def post(self, request, post_id):
        post = get_object_or_404(Post, public_uuid=post_id)
        
        # Vérifier que l'utilisateur est le propriétaire du post
        if post.author != request.user:
            return Response(
                {"error": "Vous ne pouvez pas modifier les tags de ce post"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PostTagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Récupérer les tags
        tag_uuids = serializer.validated_data['tags']
        tags = Tag.objects.filter(public_uuid__in=tag_uuids)
        
        # Retirer les tags du post
        post.tags.remove(*tags)
        
        # Retourner les tags actuels du post
        current_tags = TagSerializer(post.tags.all(), many=True)
        return Response({
            "post_id": str(post.public_uuid),
            "tags": current_tags.data
        }, status=status.HTTP_200_OK)


class TagDeleteView(APIView):
    """Supprimer un tag (admin uniquement)"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Supprime un tag spécifique",
        tags=["Tags"],
        responses={
            200: openapi.Response(description="Tag supprimé"),
            401: openapi.Response(description="Non authentifié"),
            403: openapi.Response(description="Permission refusée"),
            404: openapi.Response(description="Tag non trouvé")
        }
    )
    def delete(self, request, tag_id):
        # Vérifier que l'utilisateur est admin
        if 'admin' not in request.user.roles:
            return Response(
                {"error": "Seuls les administrateurs peuvent supprimer des tags"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tag = get_object_or_404(Tag, public_uuid=tag_id)
        tag.delete()
        
        return Response(
            {"message": "Tag supprimé avec succès"},
            status=status.HTTP_200_OK
        )
