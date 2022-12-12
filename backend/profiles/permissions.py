from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """
    Allows access only to not authenticated users.
    """

    def has_permission(self, request, view):
        return bool(not request.user.is_authenticated)
    

class IsProfileOwner(BasePermission):
    """
    Allows access only to profile owner.
    """

    def has_object_permission(self, request, view, obj):
        return bool(request.user.pk == obj.pk)
