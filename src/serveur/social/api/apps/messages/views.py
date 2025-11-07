from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ConversationView(APIView):
    @swagger_auto_schema(
        operation_description="Voir les messages échangés avec un utilisateur spécifique",
        tags=["Messages"],
        responses={
            200: openapi.Response(description="Messages trouvés"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def get(self, request, id):
        # TODO: Implémenter la récupération des messages
        
        return Response({
            "participant_id": id,
            "messages": [
                {
                    "id": 1,
                    "sender_id": 1,
                    "content": "Salut !",
                    "sent_at": "2025-11-01T10:00:00Z"
                },
                {
                    "id": 2,
                    "sender_id": id,
                    "content": "Bonjour !",
                    "sent_at": "2025-11-01T10:05:00Z"
                }
            ]
        }, status=status.HTTP_200_OK)


class ConversationsListView(APIView):
    @swagger_auto_schema(
        operation_description="Lister les conversations de l'utilisateur",
        tags=["Messages"],
        responses={
            200: openapi.Response(description="Conversations trouvées"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Récupérer les conversations réelles depuis la base de données
        return Response({
            "conversations": [
                {
                    "chat_id": 1,
                    "username": "alice",
                    "profile_picture": "https://example.com/profiles/alice.jpg"
                },
                {
                    "chat_id": 2,
                    "username": "bob",
                    "profile_picture": "https://example.com/profiles/bob.jpg"
                }
            ]
        }, status=status.HTTP_200_OK)


class CreateConversationView(APIView):
    @swagger_auto_schema(
        operation_description="Créer une nouvelle conversation avec un utilisateur",
        tags=["Messages"],
        responses={
            201: openapi.Response(description="Conversation créée"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, id):
        # TODO: Implémenter la création réelle de conversation
        return Response({
            "chat_id": 3,
            "participant_id": id,
            "created_at": "2025-11-07T12:00:00Z"
        }, status=status.HTTP_201_CREATED)


class DeleteConversationView(APIView):
    @swagger_auto_schema(
        operation_description="Supprimer une conversation avec un utilisateur spécifique",
        tags=["Messages"],
        responses={
            204: openapi.Response(description="Conversation supprimée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Conversation non trouvée")
        }
    )
    def delete(self, request, id):
        # TODO: Implémenter la suppression réelle de conversation
        return Response(status=status.HTTP_204_NO_CONTENT)
