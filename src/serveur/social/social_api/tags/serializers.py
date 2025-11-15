"""
Serializers pour l'app tags
"""
from rest_framework import serializers
from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer pour un tag"""
    
    class Meta:
        model = Tag
        fields = ['public_uuid', 'name', 'created_at']
        read_only_fields = ['public_uuid', 'created_at']


class TagCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un tag"""
    
    class Meta:
        model = Tag
        fields = ['name']
    
    def validate_name(self, value):
        """Validation du nom du tag"""
        # Nettoyer et normaliser le tag
        value = value.strip().lower()
        
        if len(value) < 2:
            raise serializers.ValidationError("Le tag doit contenir au moins 2 caractères")
        if len(value) > 30:
            raise serializers.ValidationError("Le tag ne peut pas dépasser 30 caractères")
        
        # Vérifier que le tag n'existe pas déjà
        if Tag.objects.filter(name=value).exists():
            raise serializers.ValidationError("Ce tag existe déjà")
        
        return value


class PostTagsSerializer(serializers.Serializer):
    """Serializer pour assigner/désassigner des tags à un post"""
    tags = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=10
    )
