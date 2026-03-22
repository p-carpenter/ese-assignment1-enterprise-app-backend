import django_filters
from rest_framework.exceptions import ValidationError
from rest_framework import filters, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic import RedirectView
from django.conf import settings
from django.db.models import Q
from rest_framework.throttling import ScopedRateThrottle

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
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# Song View (Browse functionality)
class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerialiser
    pagination_class = SongPagination
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly,
    ]  # must be owner to edit/delete, but anyone can read
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    search_fields = ["title", "artist", "album"]
    ordering_fields = ["title", "duration", "release_year", "uploaded_at"]
    ordering = ["title"]  # default ordering

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


# Playlist View
class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerialiser
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCollaborator]

    def get_queryset(self):
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
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        song_id = request.data.get("song_id")

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

        if not song_id:
            raise ValidationError("song_id is required.")

        remove_song_from_playlist(playlist, song_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayLogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PlayLogViewSet(viewsets.ModelViewSet):
    serializer_class = PlayLogSerialiser
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PlayLogPagination
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return PlayLog.objects.filter(user=self.request.user).order_by("-played_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Custom Redirect View for Password Reset Confirmation
class PasswordResetConfirmRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return f"{settings.FRONTEND_URL}/reset-password/confirm/{kwargs['uidb64']}/{kwargs['token']}/"


# Custom Redirect View for Email Verification Confirmation
class EmailVerificationRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return f"{settings.FRONTEND_URL}/account-confirm-email/{kwargs['key']}"
