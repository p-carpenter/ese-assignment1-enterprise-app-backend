from django.db import transaction
from django.db.models import Max
from rest_framework.exceptions import ValidationError, NotFound
from .models import Playlist, PlaylistSong, Song


@transaction.atomic
def add_song_to_playlist(playlist, song_id, user, order=None):
    """Add a song to a playlist atomically.

    If `order` is not provided, the next available order index is computed
    while locking the playlist to avoid race conditions.

    Args:
        playlist (Playlist): The target playlist instance.
        song_id (int): Primary key of the song to add.
        user (User): User adding the song (stored as `added_by`).
        order (int, optional): Explicit position to insert the song.

    Returns:
        PlaylistSong: The created through-model instance representing the
            playlist entry.

    Raises:
        NotFound: If the requested song does not exist.
        ValidationError: If the song is already present in the playlist.
    """

    try:
        song = Song.objects.get(id=song_id)
    except Song.DoesNotExist:
        raise NotFound("song not found.")

    if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
        raise ValidationError("song is already in this playlist.")

    if not order:
        # Lock the playlist row so nobody else can evaluate max_order at the same time.
        Playlist.objects.select_for_update().get(id=playlist.id)

        max_order = PlaylistSong.objects.filter(playlist=playlist).aggregate(
            Max("order")
        )["order__max"]
        order = (max_order or 0) + 1

    return PlaylistSong.objects.create(
        playlist=playlist, song=song, order=order, added_by=user
    )


def remove_song_from_playlist(playlist, song_id):
    """Remove a song from a playlist.

    Args:
        playlist (Playlist): The playlist instance to remove the song from.
        song_id (int): Primary key of the song to remove.

    Raises:
        NotFound: If the song is not present in the playlist.
    """

    try:
        playlist_song = PlaylistSong.objects.get(playlist=playlist, song_id=song_id)
        playlist_song.delete()
    except PlaylistSong.DoesNotExist:
        raise NotFound("song not found in this playlist.")
