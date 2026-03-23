from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from musicplayer.models import Song, Playlist

User = get_user_model()


class OwnershipAssignmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="uploader", email="upload@test.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

    def test_song_upload_automatically_assigns_user(self):
        data = {
            "title": "My Great Track",
            "artist": "Beethoven",
            "file_url": "https://res.cloudinary.com/mkmtszfb/test-song.mp3",
            "duration": 300,
        }

        response = self.client.post("/api/songs/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Pull it from the database to prove it saved correctly.
        song = Song.objects.get(id=response.data["id"])
        self.assertEqual(song.uploaded_by, self.user)

    def test_playlist_creation_automatically_assigns_owner(self):
        data = {"title": "My Summer Mix", "description": "Vibes", "is_public": True}

        response = self.client.post("/api/playlists/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        playlist = Playlist.objects.get(id=response.data["id"])
        self.assertEqual(playlist.owner, self.user)
