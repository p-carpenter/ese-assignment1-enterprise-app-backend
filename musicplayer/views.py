from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Song, Playlist, PlaylistSong, PlayLog
from .serialisers import (
    SongSerialiser, 
    PlaylistSerialiser, 
    PlaylistSongSerialiser, 
    PlayLogSerialiser,
)


# Song View (Browse functionality)
class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerialiser
    # Commenting out so I can test uploading without auth
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    permission_classes = [permissions.AllowAny] # Temporary for testing

    def perform_create(self, serializer):
            user = self.request.user
            
            # If user is not logged in, assign to the first admin found
            if not user.is_authenticated:
                user = User.objects.first() 
                if not user:
                    raise ValueError("No users found! Run 'python manage.py createsuperuser' first.")
                    
            serializer.save(uploaded_by=user)

# Playlist View
class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerialiser
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users see their own playlists or public playlists
        user = self.request.user
        return Playlist.objects.filter(Q(owner=user) | Q(is_public=True))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Custom Action: POST /api/playlists/{id}/add_song/
    @action(detail=True, methods=['post'])
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        
        if playlist.owner != request.user:
            return Response(
                {"detail": "You do not have permission to edit this playlist."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Pass data to the serialiser (expects 'song_id' and 'order')
        serializer = PlaylistSongSerialiser(data=request.data)
        if serializer.is_valid():
            serializer.save(playlist=playlist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Audit Log View (For History)
class PlayLogViewSet(viewsets.ModelViewSet):
    serializer_class = PlayLogSerialiser
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post'] # No updating/deleting history

    def get_queryset(self):
        # Users only see their own history
        return PlayLog.objects.filter(user=self.request.user).order_by('-played_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)