from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission allow all.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_administrator)


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_administrator
        )


class IsAdminModeratorAuthorOrCanCreateOrReadOnly(permissions.BasePermission):
    """
    Permission for comments and reviews. Allow GET to all.
    Allow POST to auth.
    Allow PATCH and DELETE to moderator, admin or author.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user == obj.author
                or request.user.is_administrator
                or request.user.is_moderator)
