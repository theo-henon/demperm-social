"""Subscriptions API views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import Forum, ForumSubscription

class SubscribeForumView(APIView):
    """POST /api/v1/subscriptions/forums/{id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="S'abonner à un forum", tags=["Subscriptions"])
    def post(self, request, id):
        forum = Forum.objects.filter(public_uuid=id).first()
        if not forum:
            return Response({'message': 'Abonnement traité'}, status=status.HTTP_200_OK)
        ForumSubscription.objects.get_or_create(user=request.user, forum=forum)
        return Response({'message': 'Abonnement réussi'}, status=status.HTTP_200_OK)

class UnsubscribeForumView(APIView):
    """DELETE /api/v1/subscriptions/forums/{id}/unsubscribe"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Se désabonner d'un forum", tags=["Subscriptions"])
    def delete(self, request, id):
        forum = Forum.objects.filter(public_uuid=id).first()
        if forum:
            ForumSubscription.objects.filter(user=request.user, forum=forum).delete()
        return Response({'message': 'Désabonnement réussi'}, status=status.HTTP_200_OK)

class SubscribeSubforumView(APIView):
    """POST /api/v1/subscriptions/subforums/{id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="S'abonner à un sous-forum", tags=["Subscriptions"])
    def post(self, request, id):
        forum = Forum.objects.filter(public_uuid=id, parent_forum__isnull=False).first()
        if not forum:
            return Response({'message': 'Abonnement traité'}, status=status.HTTP_200_OK)
        ForumSubscription.objects.get_or_create(user=request.user, forum=forum)
        return Response({'message': 'Abonnement au sous-forum réussi'}, status=status.HTTP_200_OK)

class UnsubscribeSubforumView(APIView):
    """DELETE /api/v1/subscriptions/subforums/{id}/unsubscribe"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Se désabonner d'un sous-forum", tags=["Subscriptions"])
    def delete(self, request, id):
        forum = Forum.objects.filter(public_uuid=id, parent_forum__isnull=False).first()
        if forum:
            ForumSubscription.objects.filter(user=request.user, forum=forum).delete()
        return Response({'message': 'Désabonnement du topic réussi'}, status=status.HTTP_200_OK)
