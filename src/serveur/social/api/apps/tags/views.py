"""Tags API views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.db.models import Tag, Post, PostTag
from api.db.serializers import TagSerializer
from api.common.permissions import IsOwner, IsAdmin

class TagsListView(APIView):
    """GET /api/v1/tags/"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Liste tous les tags disponibles", tags=["Tags"])
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

class TagCreateView(APIView):
    """POST /api/v1/tags/create"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Crée un nouveau tag", tags=["Tags"], request_body=TagSerializer)
    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            tag = serializer.save()
            return Response(TagSerializer(tag).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TagAssignView(APIView):
    """POST /api/v1/tags/assign/{post_id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Assigner des tags à un post", tags=["Tags"])
    def post(self, request, post_id):
        post = Post.objects.filter(public_uuid=post_id, author=request.user).first()
        if not post:
            return Response({'error': 'Post non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        tag_ids = request.data.get('tag_ids', [])
        tags = Tag.objects.filter(public_uuid__in=tag_ids)
        for tag in tags:
            PostTag.objects.get_or_create(post=post, tag=tag)
        return Response({'message': 'Tags assignés'}, status=status.HTTP_200_OK)

class TagUnassignView(APIView):
    """POST /api/v1/tags/unassign/{post_id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(operation_description="Désassigner des tags d'un post", tags=["Tags"])
    def post(self, request, post_id):
        post = Post.objects.filter(public_uuid=post_id, author=request.user).first()
        if not post:
            return Response({'error': 'Post non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        tag_ids = request.data.get('tag_ids', [])
        PostTag.objects.filter(post=post, tag__public_uuid__in=tag_ids).delete()
        return Response({'message': 'Tags désassignés'}, status=status.HTTP_200_OK)

class TagDeleteView(APIView):
    """DELETE /api/v1/tags/delete"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(operation_description="Supprime un tag spécifique", tags=["Tags"])
    def delete(self, request):
        tag_id = request.data.get('tag_id')
        Tag.objects.filter(public_uuid=tag_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
