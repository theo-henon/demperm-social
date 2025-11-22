"""Messaging serializers"""
from rest_framework import serializers
from api.db.models import Conversation, Message
from api.db.serializers import UserPublicSerializer
from api.common.validators import validate_message_content, detect_spam


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    sender = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'is_read', 'sent_at']
        read_only_fields = ['id', 'sender', 'is_read', 'sent_at']


class MessageCreateSerializer(serializers.Serializer):
    """Serializer for creating messages."""
    content = serializers.CharField(max_length=2000)
    
    def validate_content(self, value):
        validate_message_content(value)
        if detect_spam(value):
            raise serializers.ValidationError('Message appears to be spam')
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    participant1 = UserPublicSerializer(read_only=True)
    participant2 = UserPublicSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participant1', 'participant2', 'last_message', 'unread_count', 'updated_at']
        read_only_fields = fields
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-sent_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
