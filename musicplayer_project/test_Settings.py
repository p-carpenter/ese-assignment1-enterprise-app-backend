# This file imports all settings from the main settings file and then overrides specific settings for testing.
from .settings import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ACCOUNT_EMAIL_VERIFICATION = (
    "none"
)