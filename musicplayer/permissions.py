from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner.
        # Check both 'owner' and 'uploaded_by' attributes dynamically
        return (getattr(obj, "uploaded_by", None) == request.user) or (
            getattr(obj, "owner", None) == request.user
        )


class IsOwnerOrCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Owner has full permissions
        if getattr(obj, "owner", None) == request.user:
            return True

        # Private, non-collaborative playlists: owner only
        if not obj.is_public and not obj.is_collaborative:
            return False

        # Public or collaborative: reads allowed
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write actions: only add/delete songs on collaborative playlists
        if view.action in ["add_song", "delete_song"]:
            return getattr(obj, "is_collaborative", False)

        # update, partial_update, destroy: owner only
        return False
