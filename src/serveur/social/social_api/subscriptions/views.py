from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SubscribeUserView(APIView):
    @swagger_auto_schema(
        operation_description="S’abonne à un utilisateur",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Abonnement réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Abonné à l'utilisateur {id}"}, status=status.HTTP_200_OK)


class UnsubscribeUserView(APIView):
    @swagger_auto_schema(
        operation_description="Se désabonne d’un utilisateur",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Désabonnement réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def delete(self, request, id):
        return Response({"message": f"Désabonné de l'utilisateur {id}"}, status=status.HTTP_200_OK)


class SubscribeTopicView(APIView):
    @swagger_auto_schema(
        operation_description="S’abonne à un topic",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Abonnement au topic réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Topic non trouvé")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Abonné au topic {id}"}, status=status.HTTP_200_OK)


class UnsubscribeTopicView(APIView):
    @swagger_auto_schema(
        operation_description="Se désabonne d’un topic",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Désabonnement du topic réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Topic non trouvé")
        }
    )
    def delete(self, request, id):
        return Response({"message": f"Désabonné du topic {id}"}, status=status.HTTP_200_OK)


class SubscribeGroupView(APIView):
    @swagger_auto_schema(
        operation_description="S’abonne à un groupe",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Abonnement au groupe réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Groupe non trouvé")
        }
    )
    def post(self, request, id):
        return Response({"message": f"Abonné au groupe {id}"}, status=status.HTTP_200_OK)


class UnsubscribeGroupView(APIView):
    @swagger_auto_schema(
        operation_description="Se désabonne d’un groupe",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Désabonnement du groupe réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Groupe non trouvé")
        }
    )
    def delete(self, request, id):
        return Response({"message": f"Désabonné du groupe {id}"}, status=status.HTTP_200_OK)
