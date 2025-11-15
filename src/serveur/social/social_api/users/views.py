"""
Users API views.
Based on Specifications.md section 4.1.
"""
import time
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import User, Follower, AuditLog
from core.serializers import UserPublicSerializer
from core.permissions import PrivacyGuard
from .serializers import UserProfileSerializer, UserSettingsSerializer


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
        responses={200: openapi.Response(description="Profil trouvé")}
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Met à jour le profil connecté",
        tags=["Users"],
        request_body=UserProfileSerializer,
        responses={200: openapi.Response(description="Profil mis à jour")}
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
        responses={200: openapi.Response(description="Paramètres mis à jour")}
    )
    def patch(self, request):
        serializer = UserSettingsSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """GET /api/v1/users/{id}"""
    permission_classes = [IsAuthenticated, PrivacyGuard]
    
    @swagger_auto_schema(
        operation_description="Affiche le profil public d'un utilisateur",
        tags=["Users"],
        responses={200: openapi.Response(description="Profil trouvé")}
    )
    def get(self, request, id):
        user = User.objects.filter(public_uuid=id).first()
        
        if not user:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not PrivacyGuard().has_object_permission(request, self, user):
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
        responses={200: openapi.Response(description="Résultats de recherche")}
    )
    def get(self, request):
        start_time = time.time()
        query = request.GET.get('query', '').strip()
        
        if len(query) < 3:
            self._pad_response_time(start_time, 0.1)
            return Response({
                'results': [],
                'next_cursor': None
            })
        
        users = User.objects.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        ).filter(
            profile_visibility='public'
        )[:10]
        
        serializer = UserPublicSerializer(users, many=True)
        
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
        operation_description="Récupère les profils de plusieurs utilisateurs",
        tags=["Users"],
        manual_parameters=[
            openapi.Parameter(
                'ids',
                openapi.IN_QUERY,
                description="Liste d'UUIDs séparés par des virgules",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: openapi.Response(description="Profils trouvés")}
    )
    def get(self, request):
        ids_str = request.GET.get('ids', '')
        if not ids_str:
            return Response({'users': []})
        
        uuids = [u.strip() for u in ids_str.split(',') if u.strip()][:50]
        
        users = User.objects.filter(public_uuid__in=uuids)
        
        accessible_users = []
        for user in users:
            if user.profile_visibility == 'public':
                accessible_users.append(user)
            elif user.profile_visibility == 'followers':
                if Follower.objects.filter(follower=request.user, following=user).exists():
                    accessible_users.append(user)
        
        serializer = UserPublicSerializer(accessible_users, many=True)
        return Response({'users': serializer.data})


class UserDiscoverView(APIView):
    """GET /api/v1/users/discover"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Découvrir des utilisateurs",
        tags=["Users"],
        responses={200: openapi.Response(description="Utilisateurs découverts")}
    )
    def get(self, request):
        following_ids = Follower.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        
        users = User.objects.filter(
            profile_visibility='public'
        ).exclude(
            id__in=list(following_ids) + [request.user.id]
        ).order_by('-created_at')[:20]
        
        serializer = UserPublicSerializer(users, many=True)
        return Response(serializer.data)

import time
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import User, Follower, AuditLog
from core.serializers import UserPublicSerializer
from core.permissions import PrivacyGuard
from .serializers import UserProfileSerializer, UserSettingsSerializer


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
        responses={200: openapi.Response(description="Profil trouvé")}
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Met à jour le profil connecté",
        tags=["Users"],
        request_body=UserProfileSerializer,
        responses={200: openapi.Response(description="Profil mis à jour")}
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
        responses={200: openapi.Response(description="Paramètres mis à jour")}
    )
    def patch(self, request):
        serializer = UserSettingsSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """GET /api/v1/users/{id}"""
    permission_classes = [IsAuthenticated, PrivacyGuard]
    
    @swagger_auto_schema(
        operation_description="Affiche le profil public d'un utilisateur",
        tags=["Users"],
        responses={200: openapi.Response(description="Profil trouvé")}
    )
    def get(self, request, id):
        user = User.objects.filter(public_uuid=id).first()
        
        if not user:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not PrivacyGuard().has_object_permission(request, self, user):
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserPublicSerializer(user)
        return Response(serializer.data)


class UserSearchView(APIView):
    """GET /api/v1/users/search?username=..."""
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
        responses={200: openapi.Response(description="Résultats de recherche")}
    )
    def get(self, request):
        start_time = time.time()
        query = request.GET.get('query', '').strip()
        
        if len(query) < 3:
            self._pad_response_time(start_time, 0.1)
            return Response({
                'results': [],
                'next_cursor': None
            })
        
        users = User.objects.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        ).filter(
            profile_visibility='public'
        )[:10]
        
        serializer = UserPublicSerializer(users, many=True)
        
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


class UserPostsView(APIView):
    @swagger_auto_schema(
        operation_description="Posts d'un utilisateur",
        tags=["Posts"],
        responses={
            200: openapi.Response(description="Liste des posts"),
            404: openapi.Response(description="Utilisateur non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        from core.models import Post
        from posts.serializers import PostSerializer
        
        user = get_object_or_404(User, public_uuid=id)
        
        # Récupérer les posts publics de l'utilisateur
        posts = Post.objects.filter(
            author=user,
            visibility='public'
        ).order_by('-created_at')[:20]
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDiscoverView(APIView):
    @swagger_auto_schema(
        operation_description="Découvrir des utilisateurs (découverte)",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Utilisateurs découverts"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        from core.models import Follower
        
        # Découvrir des utilisateurs que l'utilisateur ne suit pas encore
        following_ids = Follower.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        
        # Exclure l'utilisateur actuel et ceux qu'il suit déjà
        users = User.objects.exclude(
            id__in=list(following_ids) + [request.user.id]
        ).filter(
            profile_visibility='public'
        ).order_by('-created_at')[:20]
        
        serializer = UserPublicSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSettingsView(APIView):
    @swagger_auto_schema(
        operation_description="Met à jour les paramètres de l'utilisateur connecté",
        tags=["Users"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email_notifications': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'privacy': openapi.Schema(type=openapi.TYPE_STRING),
                'language': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Paramètres mis à jour"),
            400: openapi.Response(description="Requête invalide"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def patch(self, request):
        data = request.data or {}
        email_notifications = data.get('email_notifications', True)
        privacy = data.get('privacy', 'public')
        language = data.get('language', 'fr')
        updated_settings = {
            "email_notifications": email_notifications,
            "privacy": privacy,
            "language": language
        }
        return Response(updated_settings, status=status.HTTP_200_OK)


class UserBulkView(APIView):
    @swagger_auto_schema(
        operation_description="Récupère les profils de plusieurs utilisateurs en une seule requête",
        tags=["Users"],
        manual_parameters=[
            openapi.Parameter(
                'ids',
                openapi.IN_QUERY,
                description="Liste d'IDs d'utilisateurs séparés par des virgules (ex: 1,2,3)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(description="Profils trouvés"),
            400: openapi.Response(description="Requête invalide"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        ids_str = request.GET.get('ids', '')
        if not ids_str:
            return Response({"error": "Paramètre 'ids' requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer les UUIDs
        user_uuids = [uuid.strip() for uuid in ids_str.split(',')]
        
        users = User.objects.filter(public_uuid__in=user_uuids)
        serializer = UserPublicSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
