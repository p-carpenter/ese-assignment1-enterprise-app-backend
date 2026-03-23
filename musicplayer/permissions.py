from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission that grants read access to everyone and write access
    only to the owner of the object.

    The check is compatible with models that name the owner field either
    `owner` or `uploaded_by`.
    """

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods; otherwise verify ownership.

        Args:
            request: The DRF request instance.
            view: The DRF view instance.
            obj: The object being accessed.

        Returns:
            bool: True if access is permitted, False otherwise.
        """

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
    """Permission for playlist-like objects that allows collaborators to
    add/remove songs but reserves owner-only actions for the owner.
    """

    def has_object_permission(self, request, view, obj):
        """Decide whether `request.user` may perform `view.action` on `obj`.

        Args:
            request: The DRF request instance.
            view: The DRF view instance (used to check `action`).
            obj: The playlist-like object being accessed.

        Returns:
            bool: True if the action is allowed, False otherwise.
        """

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
