from rest_framework.permissions import BasePermission


class IsSuperAdminOrStaff(BasePermission):
    """
    Allows access only to Super Admins and Staff users.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(user.is_staff or user.is_superuser or user.role == 'admin')
