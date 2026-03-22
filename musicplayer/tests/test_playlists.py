from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from musicplayer.models import Playlist, Song, PlaylistSong
from django.http import HttpRequest
from rest_framework.request import Request
from musicplayer.permissions import IsOwnerOrCollaborator

User = get_user_model()


class PlaylistIntegrationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pw")
        self.collab = User.objects.create_user(username="collab", password="pw")
        self.rando = User.objects.create_user(username="rando", password="pw")

        self.song1 = Song.objects.create(
            title="song 1",
            artist="artist",
            file_url="http://x",
            duration=100,
            uploaded_by=self.owner,
        )
        self.song2 = Song.objects.create(
            title="song 2",
            artist="artist",
            file_url="http://x",
            duration=100,
            uploaded_by=self.owner,
        )

        self.playlist = Playlist.objects.create(
            title="collab playlist",
            owner=self.owner,
            is_public=True,
            is_collaborative=True,
        )
        self.public_playlist = Playlist.objects.create(
            title="public playlist",
            owner=self.owner,
            is_public=True,
            is_collaborative=False,
        )

    def test_collaborator_can_add_song(self):
        self.client.force_authenticate(user=self.collab)
        url = f"/api/playlists/{self.playlist.id}/add_song/"
        response = self.client.post(url, {"song_id": self.song1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            PlaylistSong.objects.filter(
                playlist=self.playlist, song=self.song1
            ).exists()
        )

    def test_collaborator_cannot_patch_details(self):
        self.client.force_authenticate(user=self.collab)
        url = f"/api/playlists/{self.playlist.id}/"
        response = self.client.patch(url, {"title": "hacked title"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_random_user_cannot_add_song_to_public_playlist(self):
        # Public but not collaborative.
        self.playlist.is_collaborative = False
        self.playlist.save()

        self.client.force_authenticate(user=self.rando)
        url = f"/api/playlists/{self.playlist.id}/add_song/"
        response = self.client.post(url, {"song_id": self.song1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_duplicate_song_returns_400(self):
        PlaylistSong.objects.create(playlist=self.playlist, song=self.song1, order=1)

        self.client.force_authenticate(user=self.owner)
        url = f"/api/playlists/{self.playlist.id}/add_song/"
        response = self.client.post(url, {"song_id": self.song1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_song_works(self):
        PlaylistSong.objects.create(playlist=self.playlist, song=self.song1, order=1)

        self.client.force_authenticate(user=self.owner)
        url = f"/api/playlists/{self.playlist.id}/delete_song/"
        response = self.client.delete(url, {"song_id": self.song1.id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            PlaylistSong.objects.filter(
                playlist=self.playlist, song=self.song1
            ).exists()
        )

    def test_delete_nonexistent_song_returns_404(self):
        self.client.force_authenticate(user=self.owner)
        url = f"/api/playlists/{self.playlist.id}/delete_song/"
        response = self.client.delete(url, {"song_id": self.song2.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_song_missing_id_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f"/api/playlists/{self.playlist.id}/add_song/", {})
        self.assertEqual(response.status_code, 400)

    def test_add_song_invalid_id_returns_404(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f"/api/playlists/{self.playlist.id}/add_song/", {"song_id": 99999}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_song_missing_id_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f"/api/playlists/{self.playlist.id}/delete_song/")
        self.assertEqual(response.status_code, 400)

    def test_safe_methods_on_public_playlist_for_non_owner(self):
        self.client.force_authenticate(user=self.rando)
        response = self.client.get(f"/api/playlists/{self.public_playlist.id}/")
        self.assertEqual(response.status_code, 200)

    def test_private_playlist_permission_denied_for_non_owner(self):
        private_playlist = Playlist.objects.create(
            title="strictly private",
            owner=self.owner,
            is_public=False,
            is_collaborative=False,
        )

        django_request = HttpRequest()
        django_request.method = "GET"
        django_request.user = self.rando
        drf_request = Request(django_request)

        permission = IsOwnerOrCollaborator()

        has_perm = permission.has_object_permission(drf_request, None, private_playlist)
        self.assertFalse(has_perm)
