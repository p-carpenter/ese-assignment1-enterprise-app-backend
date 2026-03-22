from django.test import TestCase
from django.contrib.auth import get_user_model
from musicplayer.models import Song, Playlist

User = get_user_model()


class MusicModelTests(TestCase):
    def test_song_str(self):
        user = User.objects.create_user(username="testuser", password="pw")
        song = Song.objects.create(
            title="My Song",
            duration=100,
            file_url="https://res.cloudinary.com/mkmtszfb/test.mp3",
            uploaded_by=user,
        )
        self.assertEqual(str(song), "My Song")

    def test_playlist_str(self):
        user = User.objects.create_user(username="testuser", password="pw")
        playlist = Playlist.objects.create(title="My Playlist", owner=user)
        self.assertEqual(str(playlist), "My Playlist")
