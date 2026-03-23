from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Django AppConfig for the `users` application.

    This class registers the app with Django and can be used to configure
    application-specific initialization in the future.

    Attributes:
        name (str): The dotted Python path to the application.
    """

    name = "users"
