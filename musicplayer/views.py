from rest_framework import viewsets, permissions
from .models import Song
from .serialisers import SongSerializer

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Security Requirement

    def perform_create(self, serializer):
        # Automatically set the uploader to the current user
        serializer.save(uploaded_by=self.request.user)