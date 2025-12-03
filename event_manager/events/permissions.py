from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Only organizer can update/delete event.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "organizer", None) == request.user


class IsInvitedOrPublic(permissions.BasePermission):
    """
    Private events: only organizer or invited users can access.
    Public events: open.
    """

    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        if not request.user.is_authenticated:
            return False
        if obj.organizer == request.user:
            return True
        return obj.invited_users.filter(id=request.user.id).exists()
