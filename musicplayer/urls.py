from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SongViewSet, PlaylistViewSet, PlayLogViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'songs', SongViewSet)           # /api/songs/
router.register(r'playlists', PlaylistViewSet, basename='playlist') # /api/playlists/
router.register(r'history', PlayLogViewSet, basename='playlog')     # /api/history/
router.register(r'profiles', ProfileViewSet, basename='profile')    # /api/profiles/

urlpatterns = [
    path('', include(router.urls)),
]