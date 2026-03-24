import time
import django_filters
from rest_framework.exceptions import ValidationError
from rest_framework import filters, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic import RedirectView
from django.conf import settings
from django.db.models import Q
from rest_framework.throttling import ScopedRateThrottle
import cloudinary.utils
from rest_framework.views import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from musicplayer.services import add_song_to_playlist, remove_song_from_playlist
from .permissions import IsOwnerOrReadOnly, IsOwnerOrCollaborator
from .models import Song, Playlist, PlayLog
from .serialisers import (
    SongSerialiser,
    PlaylistSerialiser,
    PlaylistSongSerialiser,
    PlayLogSerialiser,
)
from rest_framework.pagination import PageNumberPagination


class SongPagination(PageNumberPagination):
    """Pagination for song listing endpoints with sensible defaults.

    Attributes:
        page_size (int): Default number of items per page.
        page_size_query_param (str): Query param to override page size.
        max_page_size (int): Maximum allowed page size.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# Song View (Browse functionality)
class SongViewSet(viewsets.ModelViewSet):
    """ViewSet for browsing and managing `Song` instances.

    Supports list, retrieve, create, update and delete actions. Read access is
    available to authenticated users while write access is restricted by the
    `IsOwnerOrReadOnly` permission. Provides search, ordering and pagination
    configuration for convenient browsing.

    Attributes:
        queryset: Base queryset for Song objects, optimized with select_related.
        serializer_class: Serialiser for Song instances.
        pagination_class: Pagination configuration for song listing.
        permission_classes: Permissions controlling access to song endpoints.
        filter_backends: Backends for filtering, ordering and searching songs.
        search_fields: Fields that can be searched via the search filter.
        ordering_fields: Fields that can be used for ordering results.
        ordering: Default ordering for song listings.
    """

    queryset = Song.objects.select_related("uploaded_by").all()
    serializer_class = SongSerialiser
    pagination_class = SongPagination
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly,
    ]  # Must be owner to edit/delete, but anyone can read.
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    search_fields = ["title", "artist", "album"]
    ordering_fields = ["title", "duration", "release_year", "uploaded_at"]
    ordering = ["title"]  # default ordering

    def perform_create(self, serializer):
        """Set the `uploaded_by` field to the current user on create.

        Args:
            serializer: The serialiser instance used to create the model.
        """

        serializer.save(uploaded_by=self.request.user)

    def get_throttles(self):
        """Return throttles used for the current action.

        Only throttle uploads (create action) with the `song_upload` scope.
        """

        # Only throttle the creation of new songs.
        if self.action == "create":
            self.throttle_scope = "song_upload"
            return [ScopedRateThrottle()]
        # Fall back to default global throttles for browsing.
        return super().get_throttles()


# Playlist View
class PlaylistViewSet(viewsets.ModelViewSet):
    """ViewSet for creating, listing and modifying `Playlist` objects.

    Owners may update or delete their playlists. Collaborative playlists allow
    additional users to add or remove songs (controlled by
    `IsOwnerOrCollaborator`). Exposes custom actions `add_song` and
    `delete_song` to manage playlist contents.

    Attributes:
        serializer_class: Serialiser for Playlist instances.
        permission_classes: Permissions controlling access to playlist endpoints.
    """

    serializer_class = PlaylistSerialiser
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCollaborator]

    def get_queryset(self):
        """Return playlists visible to the requesting user.

        Includes playlists owned by the user or those marked as public. The
        queryset is optimised with select_related and prefetch_related.
        """

        user = self.request.user
        return (
            Playlist.objects.filter(Q(owner=user) | Q(is_public=True))
            .select_related("owner")
            .prefetch_related(
                "playlistsong_set__song",
                "playlistsong_set__added_by",
                "playlistsong_set__song__uploaded_by",
            )
            .distinct()
        )

    def perform_create(self, serializer):
        """Assign the requesting user as the `owner` when creating a playlist."""

        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get("song_id")

        """API action to add a song to this playlist.

        Expects `song_id` in the request data and optionally `order`.
        """

        if not song_id:
            raise ValidationError("song_id is required.")

        playlist_song = add_song_to_playlist(
            playlist=playlist,
            song_id=song_id,
            user=request.user,
            order=request.data.get("order"),
        )

        serializer = PlaylistSongSerialiser(playlist_song)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"])
    def delete_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.query_params.get("song_id") or request.data.get("song_id")

        """API action to remove a song from this playlist.

        Accepts `song_id` either as a query parameter or in the request body.
        """

        if not song_id:
            raise ValidationError("song_id is required.")

        remove_song_from_playlist(playlist, song_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayLogPagination(PageNumberPagination):
    """Pagination for play log endpoints with sensible defaults.

    Attributes:
        page_size (int): Default number of items per page.
        page_size_query_param (str): Query param to override page size.
        max_page_size (int): Maximum allowed page size.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PlayLogViewSet(viewsets.ModelViewSet):
    """ViewSet for a user's `PlayLog` entries.

    Allows listing and creating play log entries. The queryset is limited to
    entries belonging to the requesting user; creating an entry sets the
    `user` automatically to the requester. Only `get` and `post` methods are
    permitted.

    Attributes:
        serializer_class: Serialiser for PlayLog instances.
        permission_classes: Permissions controlling access to play log endpoints.
        pagination_class: Pagination configuration for play log listing.
        throttle_classes: Throttling configuration to prevent spammy play logs.
        throttle_scope: Throttle scope name for play log creation.
    """

    serializer_class = PlayLogSerialiser
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PlayLogPagination
    http_method_names = ["get", "post"]

    def get_queryset(self):
        """Return play log entries for the current user ordered by time.

        Only entries belonging to the requesting user are returned.
        """

        return PlayLog.objects.filter(user=self.request.user).order_by("-played_at")

    def perform_create(self, serializer):
        """Set the `user` on newly created PlayLog entries to the current user."""

        serializer.save(user=self.request.user)

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "playlog_spam"


# Custom Redirect View for Password Reset Confirmation.
class PasswordResetConfirmRedirectView(RedirectView):
    """Redirect view to handle password reset confirmation links.

    This view is used in the password reset workflow to redirect users to the
    frontend application with the necessary parameters for confirming their password reset.

    Attributes:
        permanent (bool): Whether the redirect is permanent (HTTP 302).
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """Build the frontend URL for password reset confirmation.

        The view expects `uidb64` and `token` kwargs provided by Django's
        password reset workflow and redirects to the corresponding
        frontend route.
        """

        return f"{settings.FRONTEND_URL}/reset-password/confirm/{kwargs['uidb64']}/{kwargs['token']}/"


# Custom Redirect View for Email Verification Confirmation.
class EmailVerificationRedirectView(RedirectView):
    """Redirect view to handle email verification confirmation links.

    This view is used in the email verification workflow to redirect users to the
    frontend application with the necessary parameters for confirming their email address.
    Attributes:
    permanent (bool): Whether the redirect is permanent (HTTP 302).
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """Build the frontend URL for email verification confirmation.

        The view expects a `key` kwarg from the email verification flow and
        redirects to the frontend confirmation route.
        """

        return f"{settings.FRONTEND_URL}/account-confirm-email/{kwargs['key']}"


class CloudinarySignatureView(GenericAPIView):
    """View to generate a signature for Cloudinary uploads.

    This view is protected and requires authentication. It generates a SHA-1
    signature using the Cloudinary API secret and returns it along with the
    API key and timestamp for the frontend to use in direct uploads to Cloudinary.

    Attributes:
        permission_classes: Permissions controlling access to this endpoint.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        timestamp = int(time.time())

        params_to_sign = {"timestamp": timestamp, "folder": "prod"}

        # Generate the SHA-1 signature using the backend secret.
        signature = cloudinary.utils.api_sign_request(
            params_to_sign, settings.CLOUDINARY_API_SECRET
        )

        return Response(
            {
                "signature": signature,
                "timestamp": timestamp,
                "api_key": settings.CLOUDINARY_API_KEY,
            }
        )


@ensure_csrf_cookie
def set_csrf_token(request):
    """
    Endpoint for the React SPA to request a CSRF cookie.

    Args:
        request: The incoming HTTP request.

    Returns:
        JsonResponse: A simple JSON response indicating the CSRF cookie has been set.
    """
    return JsonResponse({"detail": "CSRF cookie set successfully"})
