from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model extending Django's `AbstractUser`.

    Adds an optional `avatar_url` field for storing a link to the user's
    avatar image.

    Attributes:
        avatar_url (str): Optional URL to the user's avatar image.
    """

    # Username or email come from AbstractUser, they are already there.
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        """Return a human-readable representation of the user.

        Returns:
            str: The user's username.
        """

        return self.username
