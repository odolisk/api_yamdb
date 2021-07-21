from rest_framework import permissions

MODERATOR = 'moderator'
ADMIN = 'admin'


class IsAdmin(permissions.IsAuthenticated):

    """
    Permission allow all.
    """
    def has_permission(self, request, view):
        auth_permission = super().has_permission(request, view)
        return (
            auth_permission
            and ((request.user.role == ADMIN) or request.user.is_superuser))


class IsAdminOrReadOnly(IsAdmin):

    def has_permission(self, request, view):
        admin_permission = super().has_permission(request, view)
        return (
            request.method == 'GET'
            or admin_permission
        )


class CommentAndReviewPermissions(permissions.IsAuthenticated):
    """
    Permission for comments and reviews. Allow GET to all.
    Allow POST to auth.
    Allow PATCH and DELETE to moderator, admin or author.
    """
    def has_permission(self, request, view):
        auth = super().has_permission(request, view)
        if (request.method == 'GET'
            or (auth and request.method == 'POST')
                or (auth and request.method in ('PATCH', 'DELETE'))):
            return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        if request.method in ('PATCH', 'DELETE'):
            return (request.user == obj.author
                    or request.user.role == ADMIN
                    or request.user.role == MODERATOR
                    or request.user.is_superuser)
