"""
Serializers pour l'app followers
"""
from rest_framework import serializers
from api.db.models import Follower, FollowerRequest
from api.db.serializers import UserPublicSerializer


class FollowerSerializer(serializers.ModelSerializer):
    """Serializer pour un follower"""
    follower = UserPublicSerializer(read_only=True)
    following = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Follower
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']


class FollowerRequestSerializer(serializers.ModelSerializer):
    """Serializer pour une demande de follow"""
    requester = UserPublicSerializer(read_only=True)
    target = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = FollowerRequest
        fields = ['public_uuid', 'requester', 'target', 'status', 'created_at']
        read_only_fields = ['public_uuid', 'created_at', 'status']


class FollowActionSerializer(serializers.Serializer):
    """Serializer pour follow/unfollow action"""
    user_id = serializers.UUIDField(required=True)
