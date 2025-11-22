"""
Serializers pour l'app posts
"""
from rest_framework import serializers
from api.db.models import Post
from api.db.serializers import UserPublicSerializer
from api.common.validators import sanitize_post_content, validate_post_content


class PostSerializer(serializers.ModelSerializer):
    """Serializer pour un post avec détails complets"""
    author = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'public_uuid', 'author', 'title', 'content', 'visibility',
            'created_at', 'updated_at', 'version', 'subforum'
        ]
        read_only_fields = ['public_uuid', 'author', 'created_at', 'updated_at', 'version']


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un post"""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'visibility', 'subforum']
    
    def validate_content(self, value):
        """Valider et nettoyer le contenu"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le contenu ne peut pas être vide")
        
        # Valider
        validate_post_content(value)
        
        # Nettoyer
        return sanitize_post_content(value)
    
    def validate_visibility(self, value):
        """Valider la visibilité"""
        valid_choices = ['hidden', 'followers', 'public']
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Visibilité invalide. Choisissez parmi: {', '.join(valid_choices)}"
            )
        return value


class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'un post"""
    
    class Meta:
        model = Post
        fields = ['content', 'visibility']
    
    def validate_content(self, value):
        """Valider et nettoyer le contenu"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le contenu ne peut pas être vide")
        
        validate_post_content(value)
        return sanitize_post_content(value)


class PostFeedSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour le feed"""
    author = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'public_uuid', 'author', 'title', 'content', 'visibility',
            'created_at', 'version'
        ]
