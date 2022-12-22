from rest_framework.permissions import BasePermission


class IsPostAuthor(BasePermission):
    """
    Allows access only to post author.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user.pk == obj.author.pk)