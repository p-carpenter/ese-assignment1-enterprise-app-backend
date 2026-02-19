from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ACCOUNT_EMAIL_VERIFICATION = (
    "none"
)