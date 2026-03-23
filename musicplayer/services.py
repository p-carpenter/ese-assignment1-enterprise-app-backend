from django.db import transaction
from django.db.models import Max
from rest_framework.exceptions import ValidationError, NotFound
from .models import Playlist, PlaylistSong, Song


@transaction.atomic
def add_song_to_playlist(playlist, song_id, user, order=None):
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
    try:
        playlist_song = PlaylistSong.objects.get(playlist=playlist, song_id=song_id)
        playlist_song.delete()
    except PlaylistSong.DoesNotExist:
        raise NotFound("song not found in this playlist.")
