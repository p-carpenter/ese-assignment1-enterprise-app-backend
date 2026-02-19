from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from musicplayer.models import Song

User = get_user_model()


class SongPermissionTests(APITestCase):
    def setUp(self):
        # 1. Create two users
        self.user_owner = User.objects.create_user(
            username="testuser", email="owner@example.com", password="password123"
        )
        self.user_hacker = User.objects.create_user(
            username="hacker", email="hacker@example.com", password="password123"
        )

        # 2. Create a song belonging to the owner
        self.song = Song.objects.create(
            title="My Song",
            artist="The Artist",
            uploaded_by=self.user_owner,
            duration=240,
            file_url="http://cloudinary.com/fake.mp3",
        )

        # 3. The URL for this specific song detail (e.g., /api/songs/1/)
        self.detail_url = reverse("song-detail", kwargs={"pk": self.song.id})

    def test_owner_can_delete_song(self):
        """Authenticating as the owner should allow deletion"""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_song(self):
        """Authenticating as a different user should be Forbidden (403)"""
        self.client.force_authenticate(user=self.user_hacker)
        response = self.client.delete(self.detail_url)

        # This is the security test
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


def test_unauthenticated_user_cannot_view_song(self):
    """Non-authenticated users should not be able to view songs."""
    self.client.logout()  #
    response = self.client.get(self.detail_url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
