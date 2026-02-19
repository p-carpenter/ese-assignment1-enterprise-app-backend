"""
URL configuration for musicplayer_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from allauth.account.views import ConfirmEmailView
from musicplayer.views import PasswordResetConfirmRedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("musicplayer.urls")),
    

    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    re_path(
        r"^api/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),

    path(
        "api/auth/password/reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmRedirectView.as_view(),
        name="password_reset_confirm",
    ),
]
