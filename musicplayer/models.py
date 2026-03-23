from django.db import models
from django.conf import settings


# Song
class Song(models.Model):
    """Model representing an individual song.

    Attributes:
        title (str): Track title.
        artist (str): Artist name.
        album (str): Album name (optional).
        release_year (int): Year of release (optional).
        file_url (str): URL to the audio file.
        cover_art_url (str): URL to cover artwork.
        duration (int): Duration in seconds.
        uploaded_by (ForeignKey): User who uploaded the song.
        uploaded_at (datetime): Timestamp of upload.
    """

    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    file_url = models.URLField()  # Cloudinary URL
    cover_art_url = models.URLField(default="https://placehold.co/220", blank=True)
    duration = models.IntegerField(help_text="Duration in seconds")

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable representation of the song.

        Returns:
            str: The song title.
        """

        return self.title


# Playlist & Through Model
class Playlist(models.Model):
    """Model representing a collection of songs (playlist).

    Attributes:
        title (str): Playlist title.
        description (str): Optional textual description.
        owner (ForeignKey): User who owns the playlist.
        is_public (bool): Whether playlist is publicly visible.
        is_collaborative (bool): Whether collaborators can add songs.
        cover_art_url (str): URL to playlist cover art.
        songs (ManyToMany): Songs in the playlist via PlaylistSong.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    is_collaborative = models.BooleanField(default=False)
    cover_art_url = models.URLField(default="https://placehold.co/220", blank=True)
    songs = models.ManyToManyField(Song, through="PlaylistSong")

    def __str__(self):
        """Return a readable representation of the playlist.

        Returns:
            str: The playlist title.
        """

        return self.title


class PlaylistSong(models.Model):
    """Through model representing the relationship between a playlist
    and a song including ordering and who added the song.

    Attributes:
        playlist (ForeignKey): The playlist containing the song.
        song (ForeignKey): The related song.
        order (int): Position of the song in the playlist.
        added_by (ForeignKey): User who added the song (optional).
        added_at (datetime): Timestamp when added.
    """

    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="playlist_songs_added",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]


# Audit Log
class PlayLog(models.Model):
    """Audit log recording when a user plays a song.

    Attributes:
        user (ForeignKey): User who played the song.
        song (ForeignKey): Song that was played.
        played_at (datetime): Timestamp when play occurred.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
