from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from musicplayer.models import Song

User = get_user_model()


class SongViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pw")
        self.other_user = User.objects.create_user(username="other", password="pw")
        self.song1 = Song.objects.create(
            title="apple",
            artist="steve",
            file_url="http://x",
            duration=300,
            uploaded_by=self.user,
        )
        self.song2 = Song.objects.create(
            title="banana",
            artist="bob",
            file_url="http://x",
            duration=150,
            uploaded_by=self.user,
        )
        self.song3 = Song.objects.create(
            title="cherry",
            artist="steve",
            file_url="http://x",
            duration=200,
            uploaded_by=self.user,
        )

    def test_search_filter(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/songs/?search=steve")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        titles = [s["title"] for s in response.data["results"]]
        self.assertIn("apple", titles)
        self.assertIn("cherry", titles)

    def test_ordering_filter(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/songs/?ordering=-duration")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        # 300, 200, 150.
        self.assertEqual(response.data["results"][0]["title"], "apple")
        self.assertEqual(response.data["results"][1]["title"], "cherry")
        self.assertEqual(response.data["results"][2]["title"], "banana")

    def test_safe_methods_allowed_for_non_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f"/api/songs/{self.song1.id}/")
        self.assertEqual(response.status_code, 200)

    def test_song_browse_hits_default_throttle(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/songs/")
        self.assertEqual(response.status_code, 200)
