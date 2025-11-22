"""Users serializers"""
from rest_framework import serializers
from api.db.models import User
from api.db.serializers import UserPublicSerializer
from api.common.validators import (
    validate_username, validate_display_name, validate_bio, sanitize_bio
)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (own profile, full details)."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'display_name', 'bio', 'avatar_url',
            'profile_visibility', 'posts_visibility', 'allow_messages_from',
            'is_verified', 'roles', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'email', 'is_verified', 'roles', 'created_at']
    
    def validate_bio(self, value):
        if value:
            validate_bio(value)
            return sanitize_bio(value)
        return value
    
    def validate_display_name(self, value):
        if value:
            validate_display_name(value)
        return value


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user privacy settings."""
    
    class Meta:
        model = User
        fields = ['profile_visibility', 'posts_visibility', 'allow_messages_from']
