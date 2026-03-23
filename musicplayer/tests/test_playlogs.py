from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from musicplayer.models import PlayLog, Song

User = get_user_model()


class PlayLogIsolationTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="usera", password="pw")
        self.user_b = User.objects.create_user(username="userb", password="pw")
        self.song = Song.objects.create(
            title="test",
            artist="test",
            file_url="http://x",
            duration=100,
            uploaded_by=self.user_a,
        )

        PlayLog.objects.create(user=self.user_a, song=self.song)
        PlayLog.objects.create(user=self.user_b, song=self.song)
        PlayLog.objects.create(user=self.user_b, song=self.song)

    def test_playlog_isolation(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/history/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User A should only see 1 log as user B's 2 logs are isolated.
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["song"]["id"], self.song.id)

    def test_create_playlog_via_api(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post("/api/history/", {"song_id": self.song.id})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            PlayLog.objects.filter(user=self.user_a, song=self.song).exists()
        )
