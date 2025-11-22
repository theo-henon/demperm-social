"""
Serializers for blocks.
"""
from rest_framework import serializers
from api.db.models import Block, User


class BlockedUserSerializer(serializers.ModelSerializer):
    """Serializer for blocked user info."""
    user_id = serializers.UUIDField(source='public_uuid', read_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'display_name', 'avatar_url']


class BlockSerializer(serializers.ModelSerializer):
    """Serializer for block with user info."""
    blocked_user = BlockedUserSerializer(source='blocked', read_only=True)
    blocked_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Block
        fields = ['blocked_user', 'blocked_at']
