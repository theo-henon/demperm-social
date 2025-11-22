"""
Custom permissions for admin panel.
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission class that requires user to have 'admin' role.
    Based on specifications.md section 4.4 - is_admin = TRUE required.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_role('admin')
