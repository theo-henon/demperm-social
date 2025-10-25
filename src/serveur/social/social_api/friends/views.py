from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class FriendsListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste les amis de l’utilisateur connecté",
        tags=["Friends"],
        responses={
            200: openapi.Response(description="Liste des amis"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        return Response([
            {"id": 1, "username": "alice_dev"},
            {"id": 2, "username": "bob_ai"}
        ], status=status.HTTP_200_OK)


class FriendRequestsView(APIView):
    @swagger_auto_schema(
        operation_description="Récupère les demandes d’amis en cours",
        tags=["Friends"],
        responses={
            200: openapi.Response(description="Demandes d’amis"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        return Response([
            {"id": 3, "username": "charlie_net"},
            {"id": 4, "username": "diana_code"}
        ], status=status.HTTP_200_OK)


class SendFriendRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Envoie une demande d’amitié",
        tags=["Friends"],
        responses={
            200: openapi.Response(description="Demande envoyée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Demande d’amitié envoyée à l’utilisateur {id}"}, status=status.HTTP_200_OK)


class AcceptFriendRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Accepte une demande d’amitié",
        tags=["Friends"],
        responses={
            200: openapi.Response(description="Demande acceptée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Demande non trouvée")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Demande d’amitié acceptée pour l’utilisateur {id}"}, status=status.HTTP_200_OK)


class RefuseFriendRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Refuse une demande d’amitié",
        tags=["Friends"],
        responses={
            200: openapi.Response(description="Demande refusée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Demande non trouvée")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Demande d’amitié refusée pour l’utilisateur {id}"}, status=status.HTTP_200_OK)


class DeleteFriendView(APIView):
    @swagger_auto_schema(
        operation_description="Supprime un ami",
        tags=["Friends"],
        responses={
            204: openapi.Response(description="Ami supprimé"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Ami non trouvé")
        }
    )
    def delete(self, request, id):
        return Response(status=status.HTTP_204_NO_CONTENT)