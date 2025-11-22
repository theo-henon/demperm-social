"""Forums API views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.db.models import Forum, ForumSubscription, Post, AuditLog
from api.db.serializers import ForumSerializer, PostListSerializer
from api.common.permissions import IsAdmin, IsModerator


class ForumsListView(APIView):
    """GET /api/v1/forums/"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des forums",
        tags=["Forums"],
        responses={200: openapi.Response(description="Liste des forums"), 401: openapi.Response(description="Non authentifié")}
    )
    def get(self, request):
        forums = Forum.objects.filter(visibility='public', parent_forum__isnull=True)
        serializer = ForumSerializer(forums, many=True)
        return Response(serializer.data)


class ForumCreateView(APIView):
    """POST /api/v1/forums/create"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer un forum",
        tags=["Forums"],
        request_body=ForumSerializer,
        responses={201: openapi.Response(description="Forum créé"), 400: openapi.Response(description="Données invalides"), 401: openapi.Response(description="Non authentifié")}
    )
    def post(self, request):
        serializer = ForumSerializer(data=request.data)
        if serializer.is_valid():
            forum = serializer.save(created_by=request.user)
            return Response(ForumSerializer(forum).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForumDetailView(APIView):
    """GET /api/v1/forums/{id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Détails d'un forum",
        tags=["Forums"],
        responses={200: openapi.Response(description="Forum trouvé"), 401: openapi.Response(description="Non authentifié"), 404: openapi.Response(description="Forum non trouvé")}
    )
    def get(self, request, id):
        forum = Forum.objects.filter(public_uuid=id).first()
        if not forum:
            return Response({'error': 'Forum non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ForumSerializer(forum)
        return Response(serializer.data)


class ForumSubforumsListView(APIView):
    """GET /api/v1/forums/{id}/subforums"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Liste des sous-forums",
        tags=["Forums"],
        responses={200: openapi.Response(description="Liste des sous-forums"), 401: openapi.Response(description="Non authentifié"), 404: openapi.Response(description="Forum non trouvé")}
    )
    def get(self, request, id):
        forum = Forum.objects.filter(public_uuid=id).first()
        if not forum:
            return Response({'error': 'Forum non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        subforums = Forum.objects.filter(parent_forum=forum)
        serializer = ForumSerializer(subforums, many=True)
        return Response(serializer.data)


class ForumSubforumCreateView(APIView):
    """POST /api/v1/forums/{id}/subforums/create"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer un sous-forum",
        tags=["Forums"],
        request_body=ForumSerializer,
        responses={201: openapi.Response(description="Sous-forum créé"), 400: openapi.Response(description="Données invalides"), 401: openapi.Response(description="Non authentifié"), 404: openapi.Response(description="Forum non trouvé")}
    )
    def post(self, request, id):
        forum = Forum.objects.filter(public_uuid=id).first()
        if not forum:
            return Response({'error': 'Forum non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ForumSerializer(data=request.data)
        if serializer.is_valid():
            subforum = serializer.save(created_by=request.user, parent_forum=forum)
            return Response(ForumSerializer(subforum).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForumMeView(APIView):
    """GET /api/v1/forums/me"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Forums suivis par l'utilisateur",
        tags=["Forums"],
        responses={200: openapi.Response(description="Liste des forums suivis"), 401: openapi.Response(description="Non authentifié")}
    )
    def get(self, request):
        subscriptions = ForumSubscription.objects.filter(user=request.user).select_related('forum')
        forums = [sub.forum for sub in subscriptions]
        serializer = ForumSerializer(forums, many=True)
        return Response(serializer.data)


class ForumSearchView(APIView):
    """GET /api/v1/forums/search"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Recherche de forums",
        tags=["Forums"],
        manual_parameters=[openapi.Parameter('query', openapi.IN_QUERY, description="Terme de recherche", type=openapi.TYPE_STRING, required=True)],
        responses={200: openapi.Response(description="Résultats de recherche"), 401: openapi.Response(description="Non authentifié")}
    )
    def get(self, request):
        query = request.GET.get('query', '').strip()
        forums = Forum.objects.filter(name__icontains=query, visibility='public')[:20]
        serializer = ForumSerializer(forums, many=True)
        return Response(serializer.data)
