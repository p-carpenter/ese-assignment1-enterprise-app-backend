from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Admin configuration for `CustomUser`.

    Extends Django's `UserAdmin` to include the `avatar_url` field in the
    personal information and user creation forms.
    """

    # Add avatar_url to the "Personal info" section
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("avatar_url",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("avatar_url",)}),)


admin.site.register(CustomUser, CustomUserAdmin)
