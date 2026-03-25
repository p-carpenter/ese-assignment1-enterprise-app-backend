from datetime import datetime

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Song, Playlist, PlaylistSong, PlayLog

User = get_user_model()


class UserMiniSerialiser(serializers.ModelSerializer):
    """Serialiser returning a compact representation of a user.

    Provides only the fields required for embedding within other serialisers
    (id, username and avatar_url).
    """

    class Meta:
        model = User
        fields = ["id", "username", "avatar_url"]


class CustomUserSerialiser(serializers.ModelSerializer):
    """Serialiser for creating and representing the full user object.

    `email` is read-only here to avoid accidental changes during updates.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "avatar_url"]
        read_only_fields = ["email"]


class SongSerialiser(serializers.ModelSerializer):
    """Serialiser for the `Song` model including validation helpers.

    The serialiser ensures uploaded_by and uploaded_at are read-only and
    validates `duration`, `release_year`, `file_url` and `cover_art_url`.
    """

    uploaded_by = UserMiniSerialiser(read_only=True)

    class Meta:
        model = Song
        fields = "__all__"
        read_only_fields = ["uploaded_by", "uploaded_at"]

    def validate_duration(self, value):
        """Validate that duration is a positive integer.

        Args:
            value (int): Duration in seconds.

        Returns:
            int: The validated duration.

        Raises:
            serializers.ValidationError: If duration is not positive.
        """

        if value <= 0:
            raise serializers.ValidationError("Duration must be a positive integer.")
        return value

    def validate_release_year(self, value):
        """Validate the `release_year` is within a reasonable range.

        Allows None, otherwise requires the year to be between 1200 and the
        current year.

        Args:
            value (int or None): The release year to validate.

        Returns:
            int or None: The validated release year.

        Raises:
            serializers.ValidationError: If the year is outside the allowed range.
        """

        if value is not None:
            current_datetime = datetime.now()
            current_year = current_datetime.year
            if value < 1200 or value > current_year:
                raise serializers.ValidationError(
                    f"Release year must be between 1200 and {current_year}."
                )
        return value

    def validate_file_url(self, value):
        """Ensure the `file_url` is hosted on the configured Cloudinary or Jamendo domain.

        Args:
            value (str): The URL to validate.

        Returns:
            str: The validated URL.

        Raises:
            serializers.ValidationError: If URL is not on the allowed domain.
        """

        if not value.startswith("https://res.cloudinary.com/") and not value.startswith(
            "https://api.jamendo.com/"
        ):
            raise serializers.ValidationError(
                "Must be a secure Cloudinary or Jamendo url."
            )
        return value

    def validate_cover_art_url(self, value):
        """Validate `cover_art_url` is either the placeholder or hosted on Cloudinary.

        Args:
            value (str): The URL to validate.

        Returns:
            str: The validated URL.

        Raises:
            serializers.ValidationError: If URL is not on the allowed domain.
        """

        if not value:
            return "https://placehold.co/220"

        if value != "https://placehold.co/220" and not value.startswith(
            "https://res.cloudinary.com/"
        ):
            raise serializers.ValidationError("Must be a secure Cloudinary url.")

        return value


class PlaylistSongSerialiser(serializers.ModelSerializer):
    """Serialiser for the through-model `PlaylistSong`.

    Attributes:
        song: Nested read-only representation of the song in this playlist entry.
        added_by: Nested read-only representation of the user who added the song.
        song_id: Write-only field to specify the song when adding to a playlist.
    """

    song = SongSerialiser(read_only=True)
    added_by = UserMiniSerialiser(read_only=True)
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), source="song", write_only=True
    )

    class Meta:
        model = PlaylistSong
        fields = ["id", "song", "song_id", "order", "added_by", "added_at"]
        read_only_fields = ["added_by", "added_at"]


class PlaylistSerialiser(serializers.ModelSerializer):
    """Serialiser for `Playlist` including nested playlist entries.

    Validates that a private playlist cannot be collaborative.

    Attributes:
        songs: Nested read-only representation of the playlist's songs via
            the `PlaylistSongSerialiser`.
        owner: Nested read-only representation of the playlist owner.
    """

    songs = PlaylistSongSerialiser(source="playlistsong_set", many=True, read_only=True)
    owner = UserMiniSerialiser(read_only=True)

    class Meta:
        model = Playlist
        fields = [
            "id",
            "title",
            "description",
            "is_public",
            "is_collaborative",
            "cover_art_url",
            "owner",
            "songs",
        ]
        read_only_fields = ["owner"]

    def validate(self, data):
        """Perform object-level validation for playlist fields.

        Ensures that a private playlist cannot be marked collaborative.
        """

        is_public = data.get(
            "is_public", self.instance.is_public if self.instance else False
        )
        is_collaborative = data.get(
            "is_collaborative",
            self.instance.is_collaborative if self.instance else False,
        )

        if not is_public and is_collaborative:
            raise serializers.ValidationError(
                {"is_collaborative": "A private playlist cannot be collaborative."}
            )

        return data


class PlayLogSerialiser(serializers.ModelSerializer):
    """Serialiser for `PlayLog` entries recording user plays of songs.

    Attributes:
        song: Nested read-only representation of the played song.
        song_id: Write-only field to specify the song being played.
    """

    song = SongSerialiser(read_only=True)
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), source="song", write_only=True
    )

    class Meta:
        model = PlayLog
        fields = ["id", "song", "song_id", "played_at"]
        read_only_fields = ["user", "played_at"]
