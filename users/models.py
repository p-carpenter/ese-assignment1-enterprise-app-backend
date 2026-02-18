from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # username or email come from AbstractUser, they are already there
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.username