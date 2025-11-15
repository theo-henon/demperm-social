"""
Custom permissions for DRF views based on Specifications.md section 3.2.
"""
from rest_framework import permissions
from .models import Conversation, Follower


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has an 'author' or 'owner' or 'user' attribute
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Permission to allow owners or moderators to access an object.
    Used for deletion and moderation actions.
    """
    def has_object_permission(self, request, view, obj):
        # Moderators and admins can access
        if request.user.has_role('moderator') or request.user.has_role('admin'):
            return True
        
        # Owner can access
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsParticipant(permissions.BasePermission):
    """
    Permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return request.user in [obj.participant1, obj.participant2]
        # If obj is a Message, check its conversation
        elif hasattr(obj, 'conversation'):
            conv = obj.conversation
            return request.user in [conv.participant1, conv.participant2]
        return False


class PrivacyGuard(permissions.BasePermission):
    """
    Permission that enforces privacy settings for users and posts.
    Implements the logic from Specifications.md section 8.2.
    """
    def has_object_permission(self, request, view, obj):
        # Always allow if requesting own resource
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        if isinstance(obj, type(request.user)) and obj == request.user:
            return True
        
        # Moderators can see everything
        if request.user.has_role('moderator') or request.user.has_role('admin'):
            return True
        
        # User profile privacy
        from .models import User
        if isinstance(obj, User):
            if obj.profile_visibility == 'public':
                return True
            elif obj.profile_visibility == 'followers':
                # Check if request.user follows obj
                return Follower.objects.filter(follower=request.user, following=obj).exists()
            elif obj.profile_visibility == 'private':
                return False
        
        # Post privacy
        from .models import Post
        if isinstance(obj, Post):
            if obj.visibility == 'public':
                return True
            elif obj.visibility == 'followers':
                # Check if request.user follows the author
                return Follower.objects.filter(follower=request.user, following=obj.author).exists()
            elif obj.visibility == 'hidden':
                return False
        
        # Default deny
        return False


class IsModerator(permissions.BasePermission):
    """
    Permission to only allow moderators and admins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.has_role('moderator') or request.user.has_role('admin')
        )


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.has_role('admin')
