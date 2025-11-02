from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SubscribeForumView(APIView):
    @swagger_auto_schema(
        operation_description="S'abonner à un forum",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Abonnement réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Forum non trouvé")
        }
    )
    def post(self, request, id):
        # TODO: Implémenter l'abonnement au forum
        return Response({"message": f"Abonné au forum {id}"}, status=status.HTTP_200_OK)


class UnsubscribeForumView(APIView):
    @swagger_auto_schema(
        operation_description="Se désabonner d'un forum",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Désabonnement réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Forum non trouvé")
        }
    )
    def delete(self, request, id):
        return Response({"message": f"Désabonné du forum {id}"}, status=status.HTTP_200_OK)


class SubscribeSubforumView(APIView):
    @swagger_auto_schema(
        operation_description="S'abonner à un sous-forum",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Abonnement au sous-forum réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Sous-forum non trouvé")
        }
    )
    def post(self, request, id):
        # TODO: Implémenter l'abonnement au sous-forum
        return Response({"message": f"Abonné au sous-forum {id}"}, status=status.HTTP_200_OK)


class UnsubscribeSubforumView(APIView):
    @swagger_auto_schema(
        operation_description="Se désabonner d'un sous-forum",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Désabonnement du topic réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Sous-forum non trouvé")
        }
    )
    def delete(self, request, id):
        # TODO: Implémenter le désabonnement du sous-forum
        return Response({"message": f"Désabonné du sous-forum {id}"}, status=status.HTTP_200_OK)
