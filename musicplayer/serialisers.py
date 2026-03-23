from datetime import datetime

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Song, Playlist, PlaylistSong, PlayLog

User = get_user_model()


class UserMiniSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar_url"]


class CustomUserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "avatar_url"]
        read_only_fields = ["email"]


class SongSerialiser(serializers.ModelSerializer):
    uploaded_by = UserMiniSerialiser(read_only=True)

    class Meta:
        model = Song
        fields = "__all__"
        read_only_fields = ["uploaded_by", "uploaded_at"]

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be a positive integer.")
        return value

    def validate_release_year(self, value):
        if value is not None:
            current_datetime = datetime.now()
            current_year = current_datetime.year
            if value < 1200 or value > current_year:
                raise serializers.ValidationError(
                    f"Release year must be between 1200 and {current_year}."
                )
        return value

    def validate_file_url(self, value):
        allowed_domain = "https://res.cloudinary.com/mkmtszfb"
        if not value.startswith(allowed_domain):
            raise serializers.ValidationError(
                f"file_url must strictly be hosted on the Cloudinary domain ({allowed_domain})."
            )
        return value

    def validate_cover_art_url(self, value):
        allowed_domain = "https://res.cloudinary.com/mkmtszfb"
        if value and not value.startswith(allowed_domain):
            if value != "https://placehold.co/220":
                raise serializers.ValidationError(
                    f"cover_art_url must strictly be hosted on the Cloudinary domain ({allowed_domain})."
                )
        return value


class PlaylistSongSerialiser(serializers.ModelSerializer):
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
    song = SongSerialiser(read_only=True)
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), source="song", write_only=True
    )

    class Meta:
        model = PlayLog
        fields = ["id", "song", "song_id", "played_at"]
        read_only_fields = ["user", "played_at"]
