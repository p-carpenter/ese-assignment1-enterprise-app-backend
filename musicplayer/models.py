from django.db import models
from django.conf import settings

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True)
    file_url = models.URLField() # Cloudinary URL
    cover_art_url = models.URLField(blank=True)
    duration = models.IntegerField(help_text="Duration in seconds")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} by {self.artist}"
    
