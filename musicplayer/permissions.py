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
    """
    Custom permission for playlists:
    - Owners can do everything
    - For collaborative playlists, any authenticated user can add/delete songs
    - For non-collaborative playlists, only owners can add/delete songs
    - Only owners can update/delete the playlist itself
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Owner has full permissions
        if getattr(obj, "owner", None) == request.user:
            return True

        # For add_song and delete_song actions on collaborative playlists
        if view.action in ["add_song", "delete_song"]:
            return getattr(obj, "is_collaborative", False)

        # For all other write operations (update, partial_update, destroy),
        # only the owner has permission
        return False
