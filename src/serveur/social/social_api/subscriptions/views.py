"""
Views pour l'app subscriptions
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Forum, ForumSubscription
from .serializers import ForumSubscriptionSerializer


class SubscribeForumView(APIView):
    """S'abonner à un forum"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="S'abonner à un forum",
        tags=["Subscriptions"],
        responses={
            200: openapi.Response(description="Abonnement traité"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request, uuid):
        # Toujours retourner 200 pour ne pas révéler l'existence du forum
        try:
            forum = Forum.objects.get(public_uuid=uuid)
            
            # Vérifier si déjà abonné
            if not ForumSubscription.objects.filter(user=request.user, forum=forum).exists():
                ForumSubscription.objects.create(
                    user=request.user,
                    forum=forum
                )
        except Forum.DoesNotExist:
            pass  # Ne pas révéler que le forum n'existe pas
        
        return Response(
            {"message": "Abonnement traité"},
            status=status.HTTP_200_OK
        )


class UnsubscribeForumView(APIView):
    """Se désabonner d'un forum"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Se désabonner d'un forum",
        tags=["Subscriptions"],
        responses={
            204: openapi.Response(description="Désabonnement réussi"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def delete(self, request, uuid):
        try:
            forum = Forum.objects.get(public_uuid=uuid)
            ForumSubscription.objects.filter(
                user=request.user,
                forum=forum
            ).delete()
        except Forum.DoesNotExist:
            pass  # Ne pas révéler que le forum n'existe pas
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class MySubscriptionsView(APIView):
    """Liste des forums auxquels l'utilisateur est abonné"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste mes abonnements aux forums",
        tags=["Subscriptions"],
        responses={
            200: ForumSubscriptionSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        subscriptions = ForumSubscription.objects.filter(
            user=request.user
        ).select_related('forum').order_by('-created_at')
        
        serializer = ForumSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
