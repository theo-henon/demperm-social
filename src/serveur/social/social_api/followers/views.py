"""
Views pour l'app followers
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import User, Follower, FollowerRequest
from .serializers import FollowerSerializer, FollowerRequestSerializer, FollowActionSerializer


class FollowersListView(APIView):
    """Liste des followers de l'utilisateur connecté"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des followers",
        tags=["Followers"],
        responses={
            200: FollowerSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        followers = Follower.objects.filter(
            following=request.user
        ).select_related('follower')
        
        serializer = FollowerSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingListView(APIView):
    """Liste des utilisateurs suivis par l'utilisateur connecté"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des suivis",
        tags=["Followers"],
        responses={
            200: FollowerSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        following = Follower.objects.filter(
            follower=request.user
        ).select_related('following')
        
        serializer = FollowerSerializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowUserView(APIView):
    """Suivre un utilisateur (si profil public) ou envoyer une demande (si privé)"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Suivre un utilisateur",
        tags=["Followers"],
        responses={
            201: openapi.Response(description="Utilisateur suivi ou demande envoyée"),
            400: openapi.Response(description="Déjà suivi ou demande en cours"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, id):
        target_user = get_object_or_404(User, public_uuid=id)
        
        # Ne peut pas se suivre soi-même
        if target_user == request.user:
            return Response(
                {"error": "Vous ne pouvez pas vous suivre vous-même"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si déjà suivi
        if Follower.objects.filter(follower=request.user, following=target_user).exists():
            return Response(
                {"error": "Vous suivez déjà cet utilisateur"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si profil public, follow direct
        if target_user.profile_visibility == 'public':
            follower = Follower.objects.create(
                follower=request.user,
                following=target_user
            )
            serializer = FollowerSerializer(follower)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Sinon, créer une demande
        existing_request = FollowerRequest.objects.filter(
            requester=request.user,
            target=target_user,
            status='pending'
        ).first()
        
        if existing_request:
            return Response(
                {"error": "Une demande est déjà en cours"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow_request = FollowerRequest.objects.create(
            requester=request.user,
            target=target_user,
            status='pending'
        )
        
        serializer = FollowerRequestSerializer(follow_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnfollowUserView(APIView):
    """Se désabonner d'un utilisateur"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Se désabonner d'un utilisateur",
        tags=["Followers"],
        responses={
            204: openapi.Response(description="Désabonnement réussi"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Relation non trouvée")
        }
    )
    def delete(self, request, id):
        target_user = get_object_or_404(User, public_uuid=id)
        
        follower_relation = Follower.objects.filter(
            follower=request.user,
            following=target_user
        ).first()
        
        if not follower_relation:
            return Response(
                {"error": "Vous ne suivez pas cet utilisateur"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        follower_relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowerRequestsView(APIView):
    """Récupérer les demandes de followers en attente"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupère les demandes de followers en cours",
        tags=["Followers"],
        responses={
            200: FollowerRequestSerializer(many=True),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        requests_list = FollowerRequest.objects.filter(
            target=request.user,
            status='pending'
        ).select_related('requester')
        
        serializer = FollowerRequestSerializer(requests_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AcceptFollowerRequestView(APIView):
    """Accepter une demande de follower"""
    permission_classes = [IsAuthenticated]
    
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
        follow_request = get_object_or_404(
            FollowerRequest,
            public_uuid=id,
            target=request.user,
            status='pending'
        )
        
        # Créer la relation follower
        Follower.objects.create(
            follower=follow_request.requester,
            following=request.user
        )
        
        # Marquer la demande comme acceptée
        follow_request.status = 'accepted'
        follow_request.save()
        
        return Response(
            {"message": "Demande de suivi acceptée"},
            status=status.HTTP_200_OK
        )


class RefuseFollowerRequestView(APIView):
    """Refuser une demande de follower"""
    permission_classes = [IsAuthenticated]
    
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
        follow_request = get_object_or_404(
            FollowerRequest,
            public_uuid=id,
            target=request.user,
            status='pending'
        )
        
        # Marquer la demande comme refusée
        follow_request.status = 'rejected'
        follow_request.save()
        
        return Response(
            {"message": "Demande de suivi refusée"},
            status=status.HTTP_200_OK
        )
