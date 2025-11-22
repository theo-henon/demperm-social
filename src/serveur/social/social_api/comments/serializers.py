"""
Serializers for comments.
"""
from rest_framework import serializers
from core.models import Comment, User


class CommentAuthorSerializer(serializers.ModelSerializer):
    """Minimal user info for comment author."""
    user_id = serializers.UUIDField(source='public_uuid', read_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'display_name', 'avatar_url', 'is_verified']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""
    comment_id = serializers.UUIDField(source='public_uuid', read_only=True)
    user = CommentAuthorSerializer(source='author', read_only=True)
    parent_comment_id = serializers.UUIDField(source='parent_comment.public_uuid', read_only=True, allow_null=True)
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'comment_id',
            'user',
            'content',
            'parent_comment_id',
            'reply_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['comment_id', 'user', 'created_at', 'updated_at']
    
    def get_reply_count(self, obj):
        """Count non-deleted replies."""
        return obj.replies.filter(deleted_at__isnull=True).count()


class CommentCreateSerializer(serializers.Serializer):
    """Serializer for creating comments."""
    content = serializers.CharField(max_length=2000, trim_whitespace=True)
    
    def validate_content(self, value):
        """Validate and sanitize content."""
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Comment content cannot be empty.")
        return value.strip()


class CommentReplySerializer(serializers.Serializer):
    """Serializer for replying to comments."""
    content = serializers.CharField(max_length=2000, trim_whitespace=True)
    
    def validate_content(self, value):
        """Validate and sanitize content."""
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Reply content cannot be empty.")
        return value.strip()
