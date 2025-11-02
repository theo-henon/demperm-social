from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TagCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Crée un nouveau tag",
        tags=["Tags"],
        responses={
            201: openapi.Response(description="Tag créé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        return Response({
            "id": 1,
            "name": "technologie"
        }, status=status.HTTP_201_CREATED)


class TagListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste tous les tags disponibles",
        tags=["Tags"],
        responses={
            200: openapi.Response(description="Liste des tags"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        return Response([
            {"id": 1, "name": "technologie"},
            {"id": 2, "name": "écologie"},
            {"id": 3, "name": "politique"}
        ], status=status.HTTP_200_OK)


class AssignTagsToTopicView(APIView):
    @swagger_auto_schema(
        operation_description="Assigner des tags à un post",
        tags=["Tags"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'tags': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description="Liste des IDs de tags à associer"
                )
            },
            required=['tags']
        ),
        responses={
            200: openapi.Response(description="Tags assignés au post"),
            400: openapi.Response(description="Requête invalide"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Post ou tag non trouvé")
        }
    )
    def post(self, request, post_id):
        return Response({
            "post_id": post_id,
            "assigned_tags": request.data.get("tags", [])
        }, status=status.HTTP_200_OK)