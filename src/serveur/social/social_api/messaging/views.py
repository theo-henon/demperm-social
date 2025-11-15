"""
Messages/Conversations API views.
Based on Specifications.md section 4.4.
"""
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import User, Conversation, Message, ConversationDeletion, AuditLog
from core.permissions import IsParticipant
from .serializers import ConversationSerializer, MessageSerializer, MessageCreateSerializer


class ConversationsView(APIView):
    """GET /api/v1/messages/"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        deleted_conv_ids = ConversationDeletion.objects.filter(
            user=request.user
        ).values_list('conversation_id', flat=True)
        
        conversations = Conversation.objects.filter(
            Q(participant1=request.user) | Q(participant2=request.user)
        ).exclude(
            id__in=deleted_conv_ids
        ).order_by('-updated_at')[:20]
        
        serializer = ConversationSerializer(
            conversations,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'conversations': serializer.data,
            'next_cursor': None
        })


class ConversationDetailView(APIView):
    """GET /api/v1/messages/{uuid}"""
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get(self, request, uuid):
        conversation = Conversation.objects.filter(
            public_uuid=uuid
        ).first()
        
        if not conversation:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not IsParticipant().has_object_permission(request, self, conversation):
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        messages = conversation.messages.order_by('-sent_at')[:50]
        
        conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            'conversation_id': str(conversation.public_uuid),
            'messages': serializer.data,
            'next_cursor': None
        })


class MessageCreateView(APIView):
    """POST /api/v1/messages/{uuid}/create"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, uuid):
        target_user = User.objects.filter(public_uuid=uuid).first()
        
        if not target_user:
            return Response(
                {'error': 'Utilisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if target_user.allow_messages_from == 'none':
            return Response(
                {'error': 'Cet utilisateur n\'accepte pas de messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        elif target_user.allow_messages_from == 'followers':
            from core.models import Follower
            is_follower = Follower.objects.filter(
                follower=request.user,
                following=target_user
            ).exists()
            if not is_follower:
                return Response(
                    {'error': 'Vous devez suivre cet utilisateur pour lui envoyer un message'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if target_user == request.user:
            return Response(
                {'error': 'Vous ne pouvez pas vous envoyer un message'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        conversation, created = Conversation.get_or_create_conversation(
            request.user,
            target_user
        )
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=serializer.validated_data['content']
        )
        
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        
        AuditLog.objects.create(
            event_type='message.send',
            actor=request.user,
            target_type='message',
            target_id=message.id
        )
        
        return Response({
            'message_id': str(message.public_uuid),
            'conversation_id': str(conversation.public_uuid),
            'sent_at': message.sent_at
        }, status=status.HTTP_201_CREATED)


class ConversationDeleteView(APIView):
    """DELETE /api/v1/messages/{uuid}/delete"""
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def delete(self, request, uuid):
        conversation = Conversation.objects.filter(
            public_uuid=uuid
        ).first()
        
        if not conversation:
            return Response(
                {'error': 'Ressource non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not IsParticipant().has_object_permission(request, self, conversation):
            return Response(
                {'error': 'Action non autorisée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ConversationDeletion.objects.get_or_create(
            conversation=conversation,
            user=request.user
        )
        
        AuditLog.objects.create(
            event_type='conversation.delete',
            actor=request.user,
            target_type='conversation',
            target_id=conversation.id
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
