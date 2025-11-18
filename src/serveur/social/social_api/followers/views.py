"""
Followers & Following API views.
Based on Specifications.md section 4.2.
"""
import time
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import User, Follower, FollowerRequest, AuditLog
from core.serializers import UserPublicSerializer, FollowerRequestSerializer
from core.permissions import IsOwner


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


class FollowersMeView(APIView):
    """GET /api/v1/followers/me"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des followers",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Liste des followers"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Get my followers
        followers = Follower.objects.filter(following=request.user).select_related('follower')
        
        # Return list of follower users
        follower_users = [f.follower for f in followers]
        serializer = UserPublicSerializer(follower_users, many=True)
        
        return Response({
            'followers': serializer.data,
            'next_cursor': None
        })


class FollowingMeView(APIView):
    """GET /api/v1/following/me"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des suivis",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Liste des utilisateurs suivis"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Get users I'm following
        following = Follower.objects.filter(follower=request.user).select_related('following')
        
        # Return list of following users
        following_users = [f.following for f in following]
        serializer = UserPublicSerializer(following_users, many=True)
        
        return Response({
            'following': serializer.data,
            'next_cursor': None
        })


class FollowerRequestsView(APIView):
    """GET /api/v1/followers/requests"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupère les demandes de followers en cours",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Demandes de followers"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Get pending follow requests received
        requests = FollowerRequest.objects.filter(
            target=request.user,
            status='pending'
        ).select_related('requester')
        
        serializer = FollowerRequestSerializer(requests, many=True)
        
        return Response({
            'requests': serializer.data
        })


class FollowerRequestView(APIView):
    """POST /api/v1/followers/{id}/request"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Envoie une demande de suivi",
        tags=["Followers"],
        responses={
            200: openapi.Response(description="Demande envoyée"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request, id):
        start_time = time.time()
        
        # Always return generic success message (anti-enumeration)
        target_user = User.objects.filter(public_uuid=id).first()
        
        if target_user and target_user != request.user:
            # Check if already following
            if not Follower.objects.filter(follower=request.user, following=target_user).exists():
                # Check if request already exists
                existing_request = FollowerRequest.objects.filter(
                    requester=request.user,
                    target=target_user
                ).first()
                
                if not existing_request:
                    # Create new request
                    FollowerRequest.objects.create(
                        requester=request.user,
                        target=target_user,
                        status='pending'
                    )
                    
                    AuditLog.objects.create(
                        event_type='follower.request.sent',
                        actor=request.user,
                        target_type='user',
                        target_id=target_user.id,
                        ip_address=get_client_ip(request)
                    )
        
        # Constant time response
        self._pad_response_time(start_time, 0.15)
        
        return Response({
            'message': 'Demande traitée'
        }, status=status.HTTP_200_OK)
    
    def _pad_response_time(self, start_time, target_time):
        """Pad response time to prevent timing attacks."""
        elapsed = time.time() - start_time
        if elapsed < target_time:
            time.sleep(target_time - elapsed)


class FollowerAcceptView(APIView):
    """POST /api/v1/followers/{id}/accept"""
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
        # Get follower request
        follower_request = FollowerRequest.objects.filter(
            public_uuid=id,
            target=request.user,
            status='pending'
        ).first()
        
        if not follower_request:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create follower relationship
        Follower.objects.get_or_create(
            follower=follower_request.requester,
            following=request.user
        )
        
        # Update request status
        follower_request.status = 'accepted'
        follower_request.save()
        
        AuditLog.objects.create(
            event_type='follower.request.accepted',
            actor=request.user,
            target_type='user',
            target_id=follower_request.requester.id,
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'message': 'Demande acceptée'
        }, status=status.HTTP_200_OK)


class FollowerRefuseView(APIView):
    """POST /api/v1/followers/{id}/refuse"""
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
        # Get follower request
        follower_request = FollowerRequest.objects.filter(
            public_uuid=id,
            target=request.user,
            status='pending'
        ).first()
        
        if not follower_request:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update request status
        follower_request.status = 'refused'
        follower_request.save()
        
        AuditLog.objects.create(
            event_type='follower.request.refused',
            actor=request.user,
            target_type='user',
            target_id=follower_request.requester.id,
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'message': 'Demande refusée'
        }, status=status.HTTP_200_OK)


class UnfollowView(APIView):
    """DELETE /api/v1/following/{id}/unfollow"""
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
        # Get target user
        target_user = User.objects.filter(public_uuid=id).first()
        
        if not target_user:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete follower relationship
        deleted_count, _ = Follower.objects.filter(
            follower=request.user,
            following=target_user
        ).delete()
        
        if deleted_count == 0:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        AuditLog.objects.create(
            event_type='follower.unfollow',
            actor=request.user,
            target_type='user',
            target_id=target_user.id,
            ip_address=get_client_ip(request)
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
