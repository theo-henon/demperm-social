from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PostCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Créer un post",
        tags=["Posts"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Titre du post"),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description="Contenu du post"),
                'subforum_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID du sous-forum")
            },
            required=['title', 'content']
        ),
        responses={
            201: openapi.Response(description="Post créé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        # TODO: Implémenter la création de post
        title = request.data.get('title', '')
        content = request.data.get('content', '')
        subforum_id = request.data.get('subforum_id')
        
        return Response({
            "id": 100,
            "title": title,
            "content": content,
            "subforum_id": subforum_id,
            "created_at": "2025-11-02T12:00:00Z"
        }, status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Détails d'un post",
        tags=["Posts"],
        responses={
            200: openapi.Response(description="Post trouvé"),
            404: openapi.Response(description="Post non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO: Implémenter la récupération d'un post
        
        return Response({
            "id": id,
            "title": "Mon post",
            "content": "Contenu du post",
            "author": {"id": 1, "username": "theo_henon"},
            "created_at": "2025-11-01T10:00:00Z",
            "comments_count": 5
        }, status=status.HTTP_200_OK)


class PostDeleteView(APIView):
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
        # TODO: Implémenter la suppression
        
        return Response(status=status.HTTP_204_NO_CONTENT)
