import datetime

from django.test import TestCase
from musicplayer.models import Playlist, Song
from musicplayer.serialisers import (
    SongSerialiser,
    PlaylistSongSerialiser,
    PlaylistSerialiser,
    User,
)


class SongSerializerTests(TestCase):
    def test_duration_must_be_positive(self):
        data = {
            "title": "test",
            "artist": "test",
            "file_url": "http://test.com",
            "duration": -10,
        }
        serialiser = SongSerialiser(data=data)
        self.assertFalse(serialiser.is_valid())
        self.assertIn("duration", serialiser.errors)

    def test_release_year_bounds(self):
        invalid_years = [1000, datetime.datetime.now().year + 10]
        for year in invalid_years:
            data = {
                "title": "test",
                "duration": 100,
                "file_url": "https://res.cloudinary.com/mkmtszfb/test.mp3",
                "release_year": year,
            }
            serialiser = SongSerialiser(data=data)
            self.assertFalse(serialiser.is_valid(), f"Year {year} should be invalid")
            self.assertIn("release_year", serialiser.errors)

        serializer = SongSerialiser(
            data={
                "title": "test",
                "duration": 100,
                "file_url": "https://res.cloudinary.com/mkmtszfb/test.mp3",
                "release_year": datetime.datetime.now().year + 10,
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_cover_art_validation(self):
        serializer = SongSerialiser(
            data={
                "title": "test",
                "duration": 100,
                "file_url": "https://res.cloudinary.com/mkmtszfb/test.mp3",
                "cover_art_url": "https://imgur.com/bad.jpg",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("cover_art_url", serializer.errors)

    def test_file_url_validation(self):
        serializer = SongSerialiser(
            data={
                "title": "test",
                "duration": 100,
                "file_url": "https://imgur.com/bad.mp3",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("file_url", serializer.errors)

    def test_valid_data(self):
        data = {
            "title": "Valid Song",
            "duration": 200,
            "artist": "Test Artist",
            "release_year": 2020,
            "file_url": "https://res.cloudinary.com/mkmtszfb/valid.mp3",
            "cover_art_url": "https://res.cloudinary.com/mkmtszfb/art.jpg",
        }
        serialiser = SongSerialiser(data=data)
        self.assertTrue(serialiser.is_valid(), serialiser.errors)


class PlaylistSerializerTests(TestCase):
    def test_private_collaborative_fails(self):
        data = {"title": "my playlist", "is_public": False, "is_collaborative": True}
        serialiser = PlaylistSerialiser(data=data)
        self.assertFalse(serialiser.is_valid())
        self.assertIn("is_collaborative", serialiser.errors)

    def test_collaborative_validation(self):
        serializer = PlaylistSerialiser(
            data={"title": "test", "is_public": False, "is_collaborative": True}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("is_collaborative", serializer.errors)

    def test_update_validation(self):
        user = User.objects.create_user(username="testowner", password="pw")
        playlist = Playlist.objects.create(
            title="existing playlist",
            owner=user,
            is_public=False,
            is_collaborative=False,
        )

        # Test updating an existing private playlist to be collaborative.
        serializer = PlaylistSerialiser(
            instance=playlist, data={"is_collaborative": True}, partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("is_collaborative", serializer.errors)

    def test_valid_data(self):
        data = {
            "title": "My Playlist",
            "description": "A great mix",
            "is_public": True,
            "is_collaborative": False,
            "cover_art_url": "https://res.cloudinary.com/mkmtszfb/cover.jpg",
        }
        serialiser = PlaylistSerialiser(data=data)
        self.assertTrue(serialiser.is_valid(), serialiser.errors)


class PlaylistSongSerializerTests(TestCase):
    def test_valid_data(self):
        user = User.objects.create_user(username="testuser", password="pw")
        song = Song.objects.create(
            title="Test Song",
            duration=100,
            file_url="https://res.cloudinary.com/mkmtszfb/test.mp3",
            uploaded_by=user,
        )
        data = {"song_id": song.id, "order": 1}
        serialiser = PlaylistSongSerialiser(data=data)
        self.assertTrue(serialiser.is_valid(), serialiser.errors)
