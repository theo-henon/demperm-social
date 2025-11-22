"""
Serializers for likes.
"""
from rest_framework import serializers
from core.models import Like, User


class LikeUserSerializer(serializers.ModelSerializer):
    """Minimal user info for like listing."""
    user_id = serializers.UUIDField(source='public_uuid', read_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'display_name', 'avatar_url', 'is_verified']


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for likes with user info."""
    user = LikeUserSerializer(read_only=True)
    liked_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Like
        fields = ['user', 'liked_at']
