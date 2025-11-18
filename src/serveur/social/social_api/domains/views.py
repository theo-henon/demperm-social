"""Domains API views (alias for Forums with parent=None)"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import Forum
from core.serializers import ForumSerializer

class DomainsListView(APIView):
    """GET /api/v1/domains/"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Liste des domaines", tags=["Domains"])
    def get(self, request):
        domains = Forum.objects.filter(parent_forum__isnull=True, visibility='public')
        serializer = ForumSerializer(domains, many=True)
        return Response(serializer.data)

class DomainDetailView(APIView):
    """GET /api/v1/domains/{id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Détails d'un domaine", tags=["Domains"])
    def get(self, request, id):
        domain = Forum.objects.filter(public_uuid=id, parent_forum__isnull=True).first()
        if not domain:
            return Response({'error': 'Domaine non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ForumSerializer(domain)
        return Response(serializer.data)

class DomainSubforumsView(APIView):
    """GET /api/v1/domains/{id}/subforums"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Liste des sous-forums d'un domaine", tags=["Domains"])
    def get(self, request, id):
        domain = Forum.objects.filter(public_uuid=id, parent_forum__isnull=True).first()
        if not domain:
            return Response({'error': 'Domaine non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        subforums = Forum.objects.filter(parent_forum=domain)
        serializer = ForumSerializer(subforums, many=True)
        return Response(serializer.data)

class DomainSubforumCreateView(APIView):
    """POST /api/v1/domains/{id}/subforums/create"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Créer un sous-forum dans un domaine", tags=["Domains"], request_body=ForumSerializer)
    def post(self, request, id):
        domain = Forum.objects.filter(public_uuid=id, parent_forum__isnull=True).first()
        if not domain:
            return Response({'error': 'Domaine non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ForumSerializer(data=request.data)
        if serializer.is_valid():
            subforum = serializer.save(created_by=request.user, parent_forum=domain)
            return Response(ForumSerializer(subforum).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
