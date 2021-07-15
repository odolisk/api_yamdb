from rest_framework import permissions

MODERATOR = 'moderator'
ADMIN = 'admin'


class IsModerator(permissions.BasePermission):

    """
    Permission to modify and delete instances except Titles.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == MODERATOR
        )


class IsAdmin(permissions.BasePermission):

    """
    Permission allow all.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.role == ADMIN
                 or request.user.is_superuser)
        )


class IsAuthorOrReadOnly(permissions.BasePermission):

    """
    Permission to only allow authors of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author)
