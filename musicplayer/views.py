from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic import RedirectView
from django.conf import settings
from django.db.models import Q, Max
from .permissions import IsOwnerOrReadOnly
from .models import Song, Playlist, PlayLog, PlaylistSong
from .serialisers import (
    SongSerialiser,
    PlaylistSerialiser,
    PlaylistSongSerialiser,
    PlayLogSerialiser,
)


# Song View (Browse functionality)
class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerialiser
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly,
    ]  # must be owner to edit/delete, but anyone can read

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


# Playlist View
class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerialiser
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Users see their own playlists or public playlists
        user = self.request.user
        return Playlist.objects.filter(Q(owner=user) | Q(is_public=True))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Custom Action: POST /api/playlists/{id}/add_song/
    @action(detail=True, methods=["post"])
    def add_song(self, request, pk=None):
        playlist = self.get_object()

        if playlist.owner != request.user:
            return Response(
                {"detail": "You do not have permission to edit this playlist."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get song_id from query params or request body
        song_id = request.query_params.get("song_id") or request.data.get("song_id")
        if not song_id:
            return Response(
                {"detail": "song_id is required (in query params or body)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response(
                {"detail": "Song not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get the next order value (or use provided order)
        order = request.data.get("order")
        if not order:
            max_order = PlaylistSong.objects.filter(playlist=playlist).aggregate(
                Max("order")
            )["order__max"]
            order = (max_order or 0) + 1

        # Check if song is already in playlist
        if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
            return Response(
                {"detail": "Song is already in this playlist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        playlist_song = PlaylistSong.objects.create(
            playlist=playlist, song=song, order=order
        )
        serializer = PlaylistSongSerialiser(playlist_song)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Custom Action: DELETE /api/playlists/{id}/delete_song/
    @action(detail=True, methods=["delete"])
    def delete_song(self, request, pk=None):
        playlist = self.get_object()

        if playlist.owner != request.user:
            return Response(
                {"detail": "You do not have permission to edit this playlist."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Expect 'song_id' in the request (e.g., body or query params)
        song_id = request.data.get("song_id") or request.query_params.get("song_id")
        if not song_id:
            return Response(
                {"detail": "song_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            playlist_song = PlaylistSong.objects.get(playlist=playlist, song_id=song_id)
            playlist_song.delete()
            return Response(
                {"detail": "Song removed from playlist."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except PlaylistSong.DoesNotExist:
            return Response(
                {"detail": "Song not found in this playlist."},
                status=status.HTTP_404_NOT_FOUND,
            )


# Audit Log View (For History)
class PlayLogViewSet(viewsets.ModelViewSet):
    serializer_class = PlayLogSerialiser
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post"]  # No updating/deleting history

    def get_queryset(self):
        # Users only see their own history
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
