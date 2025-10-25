from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TopicCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Crée un nouveau topic",
        tags=["Topics"],
        responses={
            201: openapi.Response(description="Topic créé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        # TODO
        return Response({
            "id": 101,
            "title": "Nouveau sujet de discussion",
            "content": "Contenu du topic",
            "group_id": 5
        }, status=status.HTTP_201_CREATED)


class TopicListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste les topics",
        tags=["Topics"],
        responses={
            200: openapi.Response(description="Liste des topics"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO
        return Response([
            {"id": 1, "title": "L'impact de l'IA sur la société"},
            {"id": 2, "title": "Éthique et technologie"}
        ], status=status.HTTP_200_OK)


class TopicDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Récupère les détails d’un topic (contenu + commentaires racine)",
        tags=["Topics"],
        responses={
            200: openapi.Response(description="Détails du topic"),
            404: openapi.Response(description="Topic non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO
        return Response({
            "id": id,
            "title": "L'impact de l'IA sur la société",
            "content": "Discussion sur les effets de l'IA",
            "comments": [
                {"id": 1, "content": "Très intéressant !"},
                {"id": 2, "content": "Je pense que..."}
            ]
        }, status=status.HTTP_200_OK)


class TopicDeleteView(APIView):
    @swagger_auto_schema(
        operation_description="Supprime un topic (uniquement le créateur)",
        tags=["Topics"],
        responses={
            204: openapi.Response(description="Topic supprimé"),
            403: openapi.Response(description="Accès interdit"),
            404: openapi.Response(description="Topic non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def delete(self, request, id):
        # TODO
        return Response(status=status.HTTP_204_NO_CONTENT)
