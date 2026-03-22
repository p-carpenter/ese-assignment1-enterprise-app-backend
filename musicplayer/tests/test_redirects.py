from django.test import TestCase, override_settings
from django.urls import reverse


class RedirectViewTests(TestCase):
    @override_settings(FRONTEND_URL="https://production-frontend.com")
    def test_password_reset_redirect_url_construction(self):
        url = reverse(
            "password_reset_confirm",
            kwargs={"uidb64": "MTA", "token": "set-password-token"},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "https://production-frontend.com/reset-password/confirm/MTA/set-password-token/",
        )

    @override_settings(FRONTEND_URL="https://production-frontend.com")
    def test_email_verification_redirect_url_construction(self):
        url = reverse("account_confirm_email", kwargs={"key": "verify-me-123"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "https://production-frontend.com/account-confirm-email/verify-me-123",
        )
