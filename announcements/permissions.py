from rest_framework.permissions import BasePermission

class IsTutorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.groups.filter(
            name__in=["Tutores", "Administradores"]
        ).exists()