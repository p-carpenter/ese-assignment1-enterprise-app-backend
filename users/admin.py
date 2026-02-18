from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Add avatar_url to the "Personal info" section
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('avatar_url',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('avatar_url',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)