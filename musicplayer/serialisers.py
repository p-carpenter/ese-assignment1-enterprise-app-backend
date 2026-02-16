from rest_framework import serializers
from .models import Song

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        # The fields that the React frontend will receive
        fields = ['id', 'title', 'artist', 'album', 'file_url', 'duration', 'uploaded_by']
        read_only_fields = ['uploaded_by', 'uploaded_at']