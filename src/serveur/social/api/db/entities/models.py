"""
Core models for the social network backend.
Based on Specifications.md section 5 - Security-focused implementation with UUIDs.
"""
import uuid
import hmac
import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator, URLValidator
from django.utils import timezone


class User(AbstractUser):
    """
    Extended User model with privacy settings and UUID-based public identification.
    """
    # Public UUID for API exposure (never expose internal ID)
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    
    # Profile fields
    display_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True, validators=[URLValidator(schemes=['https'])])
    
    # Privacy settings
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('followers', 'Followers Only'),
        ('public', 'Public'),
    ]
    profile_visibility = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='followers')
    posts_visibility = models.CharField(max_length=20, choices=[('hidden', 'Hidden'), ('followers', 'Followers'), ('public', 'Public')], default='followers')
    social_graph_visibility = models.CharField(max_length=20, default='hidden', editable=False)  # Always hidden
    
    # Messaging settings
    ALLOW_MESSAGES_CHOICES = [
        ('none', 'None'),
        ('followers', 'Followers Only'),
        ('everyone', 'Everyone'),
    ]
    allow_messages_from = models.CharField(max_length=20, choices=ALLOW_MESSAGES_CHOICES, default='followers')
    
    # Verification and roles
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)
    ban_reason = models.TextField(max_length=500, blank=True, null=True)
    roles = models.JSONField(default=list, blank=True)  # ['user', 'moderator', 'admin', 'elected_official']
    
    # End-to-end encryption (E2EE)
    public_key_rsa = models.TextField(blank=True, null=True, help_text="RSA-2048 public key for encrypted messages (Base64 SPKI format)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Username validation
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]{3,30}$',
        message='Username must be 3-30 characters long and contain only letters, numbers, and underscores.'
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator],
        error_messages={'unique': 'A user with that username already exists.'}
    )
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['public_uuid']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.username
    
    def has_role(self, role):
        """Check if user has a specific role."""
        return role in (self.roles or ['user'])
    
    def is_moderator(self):
        """Check if user is a moderator or admin."""
        return self.has_role('moderator') or self.has_role('admin')


class FollowerRequest(models.Model):
    """
    Pending, accepted, or refused follower requests.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_follow_requests')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_follow_requests')
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'follower_requests'
        unique_together = [['requester', 'target']]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(requester=models.F('target')),
                name='follower_request_no_self_follow'
            )
        ]
        indexes = [
            models.Index(fields=['target', 'status']),
            models.Index(fields=['requester', 'status']),
        ]
    
    def __str__(self):
        return f"{self.requester.username} -> {self.target.username} ({self.status})"


class Follower(models.Model):
    """
    Validated follower relationship (after request accepted).
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'followers'
        unique_together = [['follower', 'following']]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='follower_no_self_follow'
            )
        ]
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Forum(models.Model):
    """
    Forum or subforum for organizing discussions.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True, validators=[URLValidator(schemes=['https'])])
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_forums')
    parent_forum = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subforums')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forums'
        indexes = [
            models.Index(fields=['public_uuid']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tags for categorizing posts.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    name = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(regex=r'^[a-z0-9_]{3,30}$', message='Tag must be lowercase alphanumeric with underscores.')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        indexes = [
            models.Index(fields=['public_uuid']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """
    User post with content integrity verification.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    title = models.CharField(
        max_length=200,
        validators=[RegexValidator(regex=r'^[\w\s.,!?\'\-]+$', message='Title contains invalid characters.')]
    )
    content = models.TextField(max_length=10000)
    
    VISIBILITY_CHOICES = [
        ('hidden', 'Hidden'),
        ('followers', 'Followers Only'),
        ('public', 'Public'),
    ]
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='followers')
    
    subforum = models.ForeignKey(Forum, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, through='PostTag', related_name='posts')
    
    # Integrity fields
    version = models.IntegerField(default=1)
    signature = models.CharField(max_length=255, blank=True)
    
    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_posts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'
        indexes = [
            models.Index(fields=['public_uuid']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['subforum', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def generate_signature(self, secret_key):
        """Generate HMAC-SHA256 signature for content integrity."""
        payload = f"{self.content}|{self.created_at.isoformat()}|{self.author_id}|{self.version}"
        return hmac.new(
            secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(self, secret_key):
        """Verify content integrity signature."""
        expected_signature = self.generate_signature(secret_key)
        return hmac.compare_digest(self.signature, expected_signature)


class PostTag(models.Model):
    """
    Many-to-many relationship between posts and tags.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'post_tags'
        unique_together = [['post', 'tag']]


class Conversation(models.Model):
    """
    1:1 conversation between two users.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p2')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        unique_together = [['participant1', 'participant2']]
        constraints = [
            models.CheckConstraint(
                check=models.Q(participant1__lt=models.F('participant2')),
                name='conversation_canonical_order'
            )
        ]
        indexes = [
            models.Index(fields=['participant1', '-updated_at']),
            models.Index(fields=['participant2', '-updated_at']),
        ]
    
    def __str__(self):
        return f"Conversation: {self.participant1.username} <-> {self.participant2.username}"
    
    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        """Get or create conversation ensuring canonical order (p1 < p2)."""
        if user1.id < user2.id:
            p1, p2 = user1, user2
        else:
            p1, p2 = user2, user1
        
        conversation, created = cls.objects.get_or_create(
            participant1=p1,
            participant2=p2
        )
        return conversation, created


class Message(models.Model):
    """
    Message within a conversation.
    Supports both plaintext and E2EE (end-to-end encrypted) messages.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    content = models.TextField(max_length=2000)  # Plaintext or encrypted content (Base64)
    is_read = models.BooleanField(default=False)
    
    # End-to-end encryption fields
    is_encrypted = models.BooleanField(default=False)
    encrypted_aes_key = models.TextField(blank=True, null=True, help_text="AES key encrypted with recipient's RSA public key (Base64)")
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['conversation', '-sent_at']),
            models.Index(fields=['sender', '-sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.sent_at}"


class ConversationDeletion(models.Model):
    """
    Track which users have deleted/hidden a conversation (soft delete per user).
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='deletions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_deletions'
        unique_together = [['conversation', 'user']]


class ForumSubscription(models.Model):
    """
    User subscription to a forum.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_subscriptions')
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forum_subscriptions'
        unique_together = [['user', 'forum']]


class Comment(models.Model):
    """
    Comments on posts with optional nesting (replies).
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    content = models.TextField(max_length=2000)
    
    # For nested replies
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_comments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        indexes = [
            models.Index(fields=['public_uuid']),
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent_comment', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Like(models.Model):
    """
    Likes on posts.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        unique_together = [['user', 'post']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['post', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class Block(models.Model):
    """
    User blocks - prevents all interactions between users.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blocks'
        unique_together = [['blocker', 'blocked']]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(blocker=models.F('blocked')),
                name='block_not_self'
            )
        ]
        indexes = [
            models.Index(fields=['blocker', '-created_at']),
            models.Index(fields=['blocked', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.blocker.username} blocks {self.blocked.username}"


class Report(models.Model):
    """
    Content reports for moderation.
    """
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    
    TARGET_TYPE_CHOICES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('user', 'User'),
    ]
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    target_id = models.UUIDField()  # Generic UUID reference
    
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(max_length=500, blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_resolved')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['reporter', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]
    
    def __str__(self):
        return f"Report by {self.reporter.username}: {self.target_type} {self.reason}"


class AuditLog(models.Model):
    """
    Append-only audit log for security-critical events.
    Retention: 2 years minimum (GDPR compliance).
    """
    event_type = models.CharField(max_length=50)  # 'post.delete', 'user.login', 'message.send', etc.
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_actions')
    
    target_type = models.CharField(max_length=50, blank=True, null=True)  # 'post', 'user', 'message'
    target_id = models.IntegerField(blank=True, null=True)  # Internal ID of the resource
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)  # Additional details (e.g., moderation reason)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['target_type', 'target_id', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} by {self.actor} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Only allow creation, not updates
        if self.pk is not None:
            raise ValueError("AuditLog entries cannot be modified after creation")
        super().save(*args, **kwargs)


class RefreshToken(models.Model):
    """
    Store refresh tokens for JWT authentication with revocation capability.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'refresh_tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def is_valid(self):
        """Check if token is still valid (not expired and not revoked)."""
        return not self.revoked and timezone.now() < self.expires_at
