from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class FollowersListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste des followers",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Liste des followers"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Implémenter la récupération des followers
        
        return Response([
            {"id": 1, "username": "follower1"},
            {"id": 2, "username": "follower2"}
        ], status=status.HTTP_200_OK)


class FollowingListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste des suivis",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Liste des utilisateurs suivis"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Implémenter la récupération des suivis
        
        return Response([
            {"id": 3, "username": "followed1"},
            {"id": 4, "username": "followed2"}
        ], status=status.HTTP_200_OK)


class FollowUserView(APIView):
    @swagger_auto_schema(
        operation_description="Suivre un utilisateur",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Utilisateur suivi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, id):
        # TODO: Implémenter le follow
        
        return Response({
            "message": f"Vous suivez maintenant l'utilisateur {id}"
        }, status=status.HTTP_200_OK)


class UnfollowUserView(APIView):
    @swagger_auto_schema(
        operation_description="Se désabonner d'un utilisateur",
        tags=["Followers"],
        responses={
            204: openapi.Response(description="Désabonnement réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def delete(self, request, id):
        # TODO: Implémenter le unfollow
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowerListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste les followers de l’utilisateur connecté",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Liste des followers"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        return Response([
            {"id": 1, "username": "alice_dev"},
            {"id": 2, "username": "bob_ai"}
        ], status=status.HTTP_200_OK)


class FollowerRequestsView(APIView):
    @swagger_auto_schema(
        operation_description="Récupère les demandes de followers en cours",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Demandes de followers"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        return Response([
            {"id": 3, "username": "charlie_net"},
            {"id": 4, "username": "diana_code"}
        ], status=status.HTTP_200_OK)


class SendFollowerRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Envoie une demande de suivi",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Demande envoyée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Demande de suivi envoyée à l’utilisateur {id}"}, status=status.HTTP_200_OK)


class AcceptFollowerRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Accepte une demande de suivi",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Demande acceptée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Demande non trouvée")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Demande de suivi acceptée pour l’utilisateur {id}"}, status=status.HTTP_200_OK)


class RefuseFollowerRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Refuse une demande de suivi",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Demande refusée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Demande non trouvée")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Demande de suivi refusée pour l’utilisateur {id}"}, status=status.HTTP_200_OK)
