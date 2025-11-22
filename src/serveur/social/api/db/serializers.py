"""
Serializers for all models with validation.
Based on Specifications.md sections 4-6.
"""
from rest_framework import serializers
from .models import (
    User, FollowerRequest, Follower, Post, Tag, PostTag,
    Forum, Conversation, Message, ForumSubscription, AuditLog
)
from .validators import (
    validate_username, validate_display_name, validate_bio,
    validate_post_title, validate_post_content, sanitize_post_content,
    sanitize_bio, validate_message_content, validate_tag_name,
    detect_spam
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate_username(self, value):
        validate_username(value)
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.roles = ['user']
        user.save()
        return user


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


class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer for public user profile (limited fields)."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'bio', 'avatar_url', 'is_verified', 'created_at']
        read_only_fields = fields


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user privacy settings."""
    
    class Meta:
        model = User
        fields = ['profile_visibility', 'posts_visibility', 'allow_messages_from']
    
    def validate_social_graph_visibility(self, value):
        # Always enforce hidden
        if value != 'hidden':
            raise serializers.ValidationError('Social graph visibility must remain hidden')
        return value


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_name(self, value):
        # Convert to lowercase
        value = value.lower()
        validate_tag_name(value)
        return value


class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    author = UserPublicSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        max_length=10
    )
    subforum_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 'visibility',
            'subforum_id', 'tags', 'tag_ids', 'version', 'signature',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'tags', 'version', 'signature', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        validate_post_title(value)
        return value
    
    def validate_content(self, value):
        validate_post_content(value)
        
        # Check for spam
        if detect_spam(value):
            raise serializers.ValidationError('Content appears to be spam')
        
        return sanitize_post_content(value)
    
    def validate_tag_ids(self, value):
        if len(value) > 10:
            raise serializers.ValidationError('Maximum 10 tags allowed per post')
        
        # Verify all tags exist
        tags = Tag.objects.filter(public_uuid__in=value)
        if tags.count() != len(value):
            raise serializers.ValidationError('One or more tags not found')
        
        return value
    
    def create(self, validated_data):
        from django.conf import settings
        
        tag_ids = validated_data.pop('tag_ids', [])
        subforum_id = validated_data.pop('subforum_id', None)
        
        # Get subforum if provided
        if subforum_id:
            subforum = Forum.objects.filter(public_uuid=subforum_id).first()
            if subforum:
                validated_data['subforum'] = subforum
        
        # Create post
        post = Post.objects.create(**validated_data)
        
        # Generate signature
        post.signature = post.generate_signature(settings.SECRET_KEY)
        post.save(update_fields=['signature'])
        
        # Add tags
        if tag_ids:
            tags = Tag.objects.filter(public_uuid__in=tag_ids)
            for tag in tags:
                PostTag.objects.create(post=post, tag=tag)
        
        return post


class PostListSerializer(serializers.ModelSerializer):
    """Lighter serializer for post lists."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    author = UserPublicSerializer(read_only=True)
    tag_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 'visibility',
            'tag_count', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_tag_count(self, obj):
        return obj.tags.count()


class FollowerRequestSerializer(serializers.ModelSerializer):
    """Serializer for follower requests."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    requester = UserPublicSerializer(read_only=True)
    target = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = FollowerRequest
        fields = ['id', 'requester', 'target', 'status', 'created_at']
        read_only_fields = fields


class FollowerSerializer(serializers.ModelSerializer):
    """Serializer for follower relationships."""
    follower = UserPublicSerializer(read_only=True)
    following = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Follower
        fields = ['follower', 'following', 'created_at']
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    sender = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'is_read', 'sent_at']
        read_only_fields = ['id', 'sender', 'is_read', 'sent_at']
    
    def validate_content(self, value):
        validate_message_content(value)
        
        # Check for spam
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
        # Count unread messages for current user
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class ForumSerializer(serializers.ModelSerializer):
    """Serializer for forums."""
    id = serializers.UUIDField(source='public_uuid', read_only=True)
    created_by = UserPublicSerializer(read_only=True)
    post_count = serializers.SerializerMethodField()
    subscriber_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Forum
        fields = [
            'id', 'name', 'description', 'icon_url', 'visibility',
            'created_by', 'post_count', 'subscriber_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'post_count', 'subscriber_count', 'created_at']
    
    def get_post_count(self, obj):
        return obj.posts.filter(deleted_at__isnull=True).count()
    
    def get_subscriber_count(self, obj):
        return obj.subscriptions.count()


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs (admin only)."""
    actor = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'event_type', 'actor', 'target_type', 'target_id',
            'ip_address', 'user_agent', 'payload', 'created_at'
        ]
        read_only_fields = fields
