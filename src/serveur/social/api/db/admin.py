"""
Django admin configuration for database models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .entities.models import (
    User, Forum, Post, Comment, Like, Block, Follower, FollowerRequest,
    Message, Report, RefreshToken, AuditLog, Tag, PostTag,
    ForumSubscription
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'roles', 'created_at']
    search_fields = ['username', 'email', 'display_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('public_uuid', 'display_name', 'bio', 'avatar_url', 'roles', 'is_verified', 'public_key_rsa')
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'posts_visibility', 'allow_messages_from')
        }),
        ('Ban Info', {
            'fields': ('is_banned', 'banned_until', 'ban_reason')
        }),
    )


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'visibility', 'parent_forum', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'subforum', 'visibility', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['title', 'content']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'author', 'post', 'parent_comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['target_type', 'reason', 'reporter', 'status', 'created_at']
    list_filter = ['target_type', 'reason', 'status', 'created_at']
    search_fields = ['description']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'actor', 'ip_address', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['event_type', 'ip_address']


# Register other models with default admin
admin.site.register(Like)
admin.site.register(Block)
admin.site.register(Follower)
admin.site.register(FollowerRequest)
admin.site.register(Message)
admin.site.register(RefreshToken)
admin.site.register(Tag)
admin.site.register(PostTag)
admin.site.register(ForumSubscription)
