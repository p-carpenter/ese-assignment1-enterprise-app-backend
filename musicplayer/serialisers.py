from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Song, Playlist, PlaylistSong, PlayLog

User = get_user_model()


class CustomUserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "avatar_url"]
        read_only_fields = ["email"]


class SongSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = "__all__"
        read_only_fields = ["uploaded_by", "uploaded_at"]


class PlaylistSongSerialiser(serializers.ModelSerializer):
    song = SongSerialiser(read_only=True)
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), source="song", write_only=True
    )

    class Meta:
        model = PlaylistSong
        fields = ["id", "song", "song_id", "order", "added_at"]


class PlaylistSerialiser(serializers.ModelSerializer):
    songs = PlaylistSongSerialiser(source="playlistsong_set", many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ["id", "title", "description", "is_public", "owner", "songs"]
        read_only_fields = ["owner"]


class PlayLogSerialiser(serializers.ModelSerializer):
    class Meta:
        model = PlayLog
        fields = ["id", "song", "played_at"]
        read_only_fields = ["user", "played_at"]
