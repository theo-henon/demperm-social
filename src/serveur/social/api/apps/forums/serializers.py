"""
Serializers pour l'app forums
"""
from rest_framework import serializers
from api.db.models import Forum
from api.db.serializers import UserPublicSerializer


class ForumSerializer(serializers.ModelSerializer):
    """Serializer pour un forum"""
    created_by = UserPublicSerializer(read_only=True)
    parent_forum_uuid = serializers.UUIDField(source='parent_forum.public_uuid', read_only=True, allow_null=True)
    
    class Meta:
        model = Forum
        fields = [
            'public_uuid',
            'name',
            'description',
            'created_by',
            'parent_forum_uuid',
            'visibility',
            'created_at'
        ]
        read_only_fields = ['public_uuid', 'created_by', 'created_at']


class ForumCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un forum"""
    parent_forum_uuid = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = Forum
        fields = ['name', 'description', 'parent_forum_uuid']
    
    def validate_name(self, value):
        """Validation du nom du forum"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le nom doit contenir au moins 3 caractères")
        if len(value) > 100:
            raise serializers.ValidationError("Le nom ne peut pas dépasser 100 caractères")
        return value.strip()
    
    def validate_description(self, value):
        """Validation de la description"""
        if value and len(value) > 500:
            raise serializers.ValidationError("La description ne peut pas dépasser 500 caractères")
        return value


class ForumUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour un forum"""
    
    class Meta:
        model = Forum
        fields = ['name', 'description']
    
    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le nom doit contenir au moins 3 caractères")
        if len(value) > 100:
            raise serializers.ValidationError("Le nom ne peut pas dépasser 100 caractères")
        return value.strip()
    
    def validate_description(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("La description ne peut pas dépasser 500 caractères")
        return value
