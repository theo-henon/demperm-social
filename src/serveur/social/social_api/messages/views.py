from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SendMessageView(APIView):
    @swagger_auto_schema(
        operation_description="Envoyer un message privé",
        tags=["Messages"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Contenu du message"
                )
            },
            required=['content']
        ),
        responses={
            201: openapi.Response(description="Message envoyé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, id):
        # TODO: Implémenter l'envoi de message
        content = request.data.get('content', '')
        
        return Response({
            "id": 1,
            "recipient_id": id,
            "content": content,
            "sent_at": "2025-11-02T12:00:00Z"
        }, status=status.HTTP_201_CREATED)


class MessageThreadView(APIView):
    @swagger_auto_schema(
        operation_description="Voir les messages échangés",
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
