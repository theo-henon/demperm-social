"""
Messages API views.
Based on Specifications.md section 4.4.
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.models import User, Conversation, Message, ConversationDeletion, AuditLog
from core.serializers import ConversationSerializer, MessageSerializer
from core.permissions import IsParticipant


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


class MessagesListView(APIView):
    """GET /api/v1/messages/"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lister les conversations de l'utilisateur",
        tags=["Messages"],
        responses={
            200: openapi.Response(description="Conversations trouvées"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        from django.db import models
        
        # Get conversations where user is participant
        conversations = Conversation.objects.filter(
            models.Q(participant1=request.user) | models.Q(participant2=request.user)
        ).exclude(
            deletions__user=request.user
        ).order_by('-updated_at')[:20]
        
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response({
            'conversations': serializer.data,
            'next_cursor': None
        })


class ConversationDetailView(APIView):
    """GET /api/v1/messages/{id}"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Voir les messages échangés avec un utilisateur spécifique",
        tags=["Messages"],
        responses={
            200: openapi.Response(description="Messages trouvés"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Conversation non trouvée")
        }
    )
    def get(self, request, id):
        from django.db import models
        
        # Get conversation
        conversation = Conversation.objects.filter(
            public_uuid=id
        ).filter(
            models.Q(participant1=request.user) | models.Q(participant2=request.user)
        ).first()
        
        if not conversation:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get messages
        messages = Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('-sent_at')[:50]
        
        # Mark messages as read
        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        return Response({
            'conversation_id': str(conversation.public_uuid),
            'messages': serializer.data,
            'next_cursor': None
        })


class MessageCreateView(APIView):
    """POST /api/v1/messages/{user_id}/create"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer une nouvelle conversation avec un utilisateur",
        tags=["Messages"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: openapi.Response(description="Conversation créée"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié"),
            403: openapi.Response(description="Utilisateur n'accepte pas les messages"),
            404: openapi.Response(description="Utilisateur non trouvé")
        }
    )
    def post(self, request, user_id):
        # Get target user
        target_user = User.objects.filter(public_uuid=user_id).first()
        
        if not target_user:
            return Response(
                {'error': 'Utilisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if target accepts messages
        if target_user.allow_messages_from == 'none':
            return Response(
                {'error': 'Cet utilisateur n\'accepte pas de messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if target_user.allow_messages_from == 'followers':
            from core.models import Follower
            if not Follower.objects.filter(follower=target_user, following=request.user).exists():
                return Response(
                    {'error': 'Cet utilisateur n\'accepte que les messages de ses followers'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get or create conversation
        conversation, created = Conversation.get_or_create_conversation(request.user, target_user)
        
        # Validate and create message
        content = request.data.get('content', '').strip()
        if not content or len(content) > 2000:
            return Response(
                {'error': 'Content must be between 1 and 2000 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()
        
        AuditLog.objects.create(
            event_type='message.sent',
            actor=request.user,
            target_type='user',
            target_id=target_user.id,
            ip_address=get_client_ip(request)
        )
        
        return Response({
            'message_id': str(message.public_uuid),
            'conversation_id': str(conversation.public_uuid),
            'sent_at': message.sent_at.isoformat()
        }, status=status.HTTP_201_CREATED)


class ConversationDeleteView(APIView):
    """DELETE /api/v1/messages/{id}/delete"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Supprimer une conversation avec un utilisateur spécifique",
        tags=["Messages"],
        responses={
            204: openapi.Response(description="Conversation supprimée"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Conversation non trouvée")
        }
    )
    def delete(self, request, id):
        from django.db import models
        
        # Get conversation
        conversation = Conversation.objects.filter(
            public_uuid=id
        ).filter(
            models.Q(participant1=request.user) | models.Q(participant2=request.user)
        ).first()
        
        if not conversation:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Soft delete for this user only
        ConversationDeletion.objects.get_or_create(
            conversation=conversation,
            user=request.user
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
