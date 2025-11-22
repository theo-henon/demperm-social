"""
Users API views.
Based on Specifications.md section 4.1.
"""
import time
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.db.models import User, Follower, AuditLog, Post
from api.db.serializers import UserPublicSerializer, UserProfileSerializer, UserSettingsSerializer, PostSerializer
from api.common.permissions import PrivacyGuard


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


class UserMeView(APIView):
    """GET/PATCH /api/v1/users/me"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupère les informations du profil connecté",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Profil trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Met à jour le profil connecté",
        tags=["Users"],
        request_body=UserProfileSerializer,
        responses={
            200: openapi.Response(description="Profil mis à jour"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            AuditLog.objects.create(
                event_type='user.profile.update',
                actor=request.user,
                target_type='user',
                target_id=request.user.id,
                ip_address=get_client_ip(request)
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSettingsView(APIView):
    """PATCH /api/v1/users/me/settings"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Met à jour les paramètres de l'utilisateur connecté",
        tags=["Users"],
        request_body=UserSettingsSerializer,
        responses={
            200: openapi.Response(description="Paramètres mis à jour"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def patch(self, request):
        serializer = UserSettingsSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """GET /api/v1/users/{id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Affiche le profil public d'un utilisateur",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Profil trouvé"),
            403: openapi.Response(description="Accès interdit"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        user = User.objects.filter(public_uuid=id).first()
        
        if not user:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check privacy guard
        privacy_guard = PrivacyGuard()
        if not privacy_guard.has_object_permission(request, self, user):
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserPublicSerializer(user)
        return Response(serializer.data)


class UserSearchView(APIView):
    """GET /api/v1/users/search?query=..."""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Recherche utilisateur par username",
        tags=["Users"],
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Terme de recherche (min 3 chars)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(description="Résultats de recherche"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        start_time = time.time()
        query = request.GET.get('query', '').strip()
        
        # Anti-enumeration: minimum 3 chars
        if len(query) < 3:
            self._pad_response_time(start_time, 0.1)
            return Response({
                'results': [],
                'next_cursor': None
            })
        
        # Search only in public profiles
        users = User.objects.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        ).filter(
            profile_visibility='public'
        )[:10]
        
        serializer = UserPublicSerializer(users, many=True)
        
        # Constant time response to prevent timing attacks
        self._pad_response_time(start_time, 0.1)
        
        return Response({
            'results': serializer.data,
            'next_cursor': None
        })
    
    def _pad_response_time(self, start_time, target_time):
        """Pad response time to prevent timing attacks."""
        elapsed = time.time() - start_time
        if elapsed < target_time:
            time.sleep(target_time - elapsed)


class UserBulkView(APIView):
    """GET /api/v1/users/bulk?ids=uuid1,uuid2,uuid3"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupère les profils de plusieurs utilisateurs en une seule requête",
        tags=["Users"],
        manual_parameters=[
            openapi.Parameter(
                'ids',
                openapi.IN_QUERY,
                description="Liste d'UUIDs séparés par des virgules (max 50)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(description="Profils trouvés"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        ids_str = request.GET.get('ids', '')
        if not ids_str:
            return Response({'users': []})
        
        # Parse UUIDs (max 50)
        uuids = [u.strip() for u in ids_str.split(',') if u.strip()][:50]
        
        users = User.objects.filter(public_uuid__in=uuids)
        
        # Filter by privacy settings
        accessible_users = []
        privacy_guard = PrivacyGuard()
        for user in users:
            if privacy_guard.has_object_permission(request, self, user):
                accessible_users.append(user)
        
        serializer = UserPublicSerializer(accessible_users, many=True)
        return Response({'users': serializer.data})


class UserDiscoverView(APIView):
    """GET /api/v1/users/discover"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Découvrir des utilisateurs (découverte)",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Utilisateurs découverts"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # Get users already followed
        following_ids = Follower.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        
        # Discover public users not yet followed
        users = User.objects.filter(
            profile_visibility='public'
        ).exclude(
            id__in=list(following_ids) + [request.user.id]
        ).order_by('-created_at')[:20]
        
        serializer = UserPublicSerializer(users, many=True)
        return Response(serializer.data)


class UserPostsView(APIView):
    """GET /api/v1/users/{id}/posts"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Posts d'un utilisateur",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Liste des posts"),
            403: openapi.Response(description="Accès interdit"),
            404: openapi.Response(description="Utilisateur non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        user = User.objects.filter(public_uuid=id).first()
        
        if not user:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check user profile privacy
        privacy_guard = PrivacyGuard()
        if not privacy_guard.has_object_permission(request, self, user):
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get posts based on visibility
        posts = Post.objects.filter(
            author=user,
            deleted_at__isnull=True
        ).filter(
            Q(visibility='public') |
            (Q(visibility='followers') & Q(author__followers__follower=request.user))
        ).distinct().order_by('-created_at')[:20]
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class UserPublicKeyView(APIView):
    """GET /api/v1/users/{user_id}/public_key - Get user's RSA public key for E2EE"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupère la clé publique RSA d'un utilisateur pour chiffrer des messages",
        tags=["Users", "E2EE"],
        responses={
            200: openapi.Response(
                description="Clé publique trouvée",
                examples={
                    "application/json": {
                        "user_id": "uuid-here",
                        "public_key_rsa": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...",
                        "key_format": "SPKI",
                        "algorithm": "RSA-2048"
                    }
                }
            ),
            404: openapi.Response(description="Utilisateur ou clé non trouvée")
        }
    )
    def get(self, request, id):
        try:
            user = User.objects.get(public_uuid=id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.public_key_rsa:
            return Response(
                {'error': 'Cet utilisateur n\'a pas configuré de clé publique'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'user_id': str(user.public_uuid),
            'username': user.username,
            'public_key_rsa': user.public_key_rsa,
            'key_format': 'SPKI',
            'algorithm': 'RSA-2048'
        })


class UserPublicKeyUploadView(APIView):
    """POST /api/v1/users/me/public_key - Upload user's RSA public key"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Envoie la clé publique RSA de l'utilisateur (générée côté client)",
        tags=["Users", "E2EE"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['public_key_rsa'],
            properties={
                'public_key_rsa': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Clé publique RSA-2048 au format SPKI Base64"
                )
            }
        ),
        responses={
            200: openapi.Response(description="Clé publique enregistrée"),
            400: openapi.Response(description="Clé invalide")
        }
    )
    def post(self, request):
        public_key = request.data.get('public_key_rsa')
        
        if not public_key:
            return Response({'error': 'public_key_rsa requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Basic validation: check if it looks like a Base64-encoded key
        if len(public_key) < 300 or not public_key.isprintable():
            return Response(
                {'error': 'Format de clé publique invalide (attendu: Base64 SPKI)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Store the public key
        request.user.public_key_rsa = public_key
        request.user.save(update_fields=['public_key_rsa'])
        
        # Log action
        AuditLog.objects.create(
            actor=request.user,
            event_type='user.public_key.upload',
            payload={'user_id': str(request.user.public_uuid)},
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'message': 'Clé publique enregistrée avec succès',
            'user_id': str(request.user.public_uuid)
        })
