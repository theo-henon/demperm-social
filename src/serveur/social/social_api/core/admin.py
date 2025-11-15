"""
Django Admin configuration for core models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, FollowerRequest, Follower, Post, Tag, PostTag,
    Forum, Conversation, Message, ConversationDeletion,
    ForumSubscription, AuditLog, RefreshToken
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'display_name', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'profile_visibility', 'created_at']
    search_fields = ['username', 'email', 'display_name']
    readonly_fields = ['public_uuid', 'created_at', 'updated_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('public_uuid', 'display_name', 'bio', 'avatar_url')
        }),
        ('Privacy', {
            'fields': ('profile_visibility', 'posts_visibility', 'allow_messages_from')
        }),
        ('Roles', {
            'fields': ('is_verified', 'roles')
        }),
    )


@admin.register(FollowerRequest)
class FollowerRequestAdmin(admin.ModelAdmin):
    list_display = ['requester', 'target', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['requester__username', 'target__username']
    readonly_fields = ['public_uuid', 'created_at', 'updated_at']


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'visibility', 'created_at', 'deleted_at']
    list_filter = ['visibility', 'created_at', 'deleted_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['public_uuid', 'version', 'signature', 'created_at', 'updated_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['public_uuid', 'created_at']


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'visibility', 'created_by', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['public_uuid', 'created_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['participant1', 'participant2', 'created_at', 'updated_at']
    search_fields = ['participant1__username', 'participant2__username']
    readonly_fields = ['public_uuid', 'created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'is_read', 'sent_at']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['public_uuid', 'sent_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'actor', 'target_type', 'target_id', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['event_type', 'actor__username']
    readonly_fields = ['event_type', 'actor', 'target_type', 'target_id', 'ip_address', 'user_agent', 'payload', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'revoked']
    list_filter = ['revoked', 'created_at', 'expires_at']
    search_fields = ['user__username']
    readonly_fields = ['token', 'created_at']


admin.site.register(PostTag)
admin.site.register(ConversationDeletion)
admin.site.register(ForumSubscription)
