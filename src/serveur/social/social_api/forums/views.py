"""
Views pour l'app forums
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import User, Forum
from .serializers import ForumSerializer, ForumCreateSerializer, ForumUpdateSerializer


class ForumListView(APIView):
    """Liste tous les forums (racine uniquement)"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des forums racine",
        tags=["Forums"],
        responses={
            200: ForumSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        forums = Forum.objects.filter(
            parent_forum__isnull=True
        ).select_related('created_by').order_by('-created_at')
        
        serializer = ForumSerializer(forums, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForumCreateView(APIView):
    """Créer un forum"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer un forum",
        tags=["Forums"],
        request_body=ForumCreateSerializer,
        responses={
            201: ForumSerializer,
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        serializer = ForumCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        parent_forum = None
        if serializer.validated_data.get('parent_forum_uuid'):
            parent_forum = get_object_or_404(
                Forum, 
                public_uuid=serializer.validated_data['parent_forum_uuid']
            )
        
        forum = Forum.objects.create(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            created_by=request.user,
            parent_forum=parent_forum
        )
        
        response_serializer = ForumSerializer(forum)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ForumDetailView(APIView):
    """Détails d'un forum"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Détails d'un forum",
        tags=["Forums"],
        responses={
            200: ForumSerializer,
            404: openapi.Response(description="Forum non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        forum = get_object_or_404(Forum, public_uuid=id)
        serializer = ForumSerializer(forum)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForumMeView(APIView):
    """Forums suivis par l'utilisateur connecté"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Forums suivis par l'utilisateur",
        tags=["Forums"],
        responses={
            200: ForumSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Implémenter avec un modèle de subscription plus tard
        # Pour l'instant, retourner une liste vide
        return Response([], status=status.HTTP_200_OK)


class ForumSearchView(APIView):
    """Recherche de forums"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Recherche de forums",
        tags=["Forums"],
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Terme de recherche",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ForumSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        query = request.GET.get('query', '').strip()
        
        if not query:
            return Response([], status=status.HTTP_200_OK)
        
        forums = Forum.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('created_by').order_by('-created_at')[:20]
        
        serializer = ForumSerializer(forums, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForumSubforumsView(APIView):
    """Liste des sous-forums d'un forum"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des sous-forums",
        tags=["Forums"],
        responses={
            200: ForumSerializer(many=True),
            404: openapi.Response(description="Forum non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        parent_forum = get_object_or_404(Forum, public_uuid=id)
        
        subforums = Forum.objects.filter(
            parent_forum=parent_forum
        ).select_related('created_by').order_by('name')
        
        serializer = ForumSerializer(subforums, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForumSubforumCreateView(APIView):
    """Créer un sous-forum"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer un sous-forum",
        tags=["Forums"],
        request_body=ForumCreateSerializer,
        responses={
            201: ForumSerializer,
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Forum parent non trouvé")
        }
    )
    def post(self, request, id):
        parent_forum = get_object_or_404(Forum, public_uuid=id)
        
        serializer = ForumCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        forum = Forum.objects.create(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            created_by=request.user,
            parent_forum=parent_forum
        )
        
        response_serializer = ForumSerializer(forum)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
