from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TopicCommentCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Ajoute un commentaire à un topic",
        tags=["Comments"],
        responses={
            201: openapi.Response(description="Commentaire ajouté"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Topic non trouvé")
        }
    )
    def post(self, request, id):
        # TODO
        return Response({
            "id": 1001,
            "content": "Très bon sujet !",
            "author": "theo_henon",
            "topic_id": id
        }, status=status.HTTP_201_CREATED)


class TopicCommentListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste les commentaires d’un topic",
        tags=["Comments"],
        responses={
            200: openapi.Response(description="Liste des commentaires"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Topic non trouvé")
        }
    )
    def get(self, request, id):
        # TODO
        return Response([
            {"id": 1, "content": "Très intéressant !", "author": "alice_dev"},
            {"id": 2, "content": "Je pense que...", "author": "bob_ai"}
        ], status=status.HTTP_200_OK)


class CommentLikeView(APIView):

    @swagger_auto_schema(
        operation_description="Like ou unlike un commentaire",
        tags=["Comments"],
        responses={
            200: openapi.Response(description="Like/unlike effectué"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Commentaire non trouvé")
        }
    )
    def post(self, request, id):
        # TODO
        return Response({"message": "Commentaire liké"}, status=status.HTTP_200_OK)


class CommentDeleteView(APIView):

    @swagger_auto_schema(
        operation_description="Supprime un commentaire",
        tags=["Comments"],
        responses={
            204: openapi.Response(description="Commentaire supprimé"),
            403: openapi.Response(description="Accès interdit"),
            404: openapi.Response(description="Commentaire non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def delete(self, request, id):
        # TODO: Ajouter logique réelle
        return Response(status=status.HTTP_204_NO_CONTENT)