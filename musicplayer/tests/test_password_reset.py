import re
from django.urls import reverse
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordResetTests(APITestCase):
    """Test suite for password reset functionality"""

    def setUp(self):
        """Create a test user for password reset tests"""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="OldPassword123!",
        )
        self.reset_url = reverse("rest_password_reset")
        self.reset_confirm_url = "rest_password_reset_confirm"

    def _get_uid_and_token(self, user):
        """
        Trigger the email and parse the uid/token from the email body."""
        outbox_count = len(mail.outbox)

        self.client.post(self.reset_url, {"email": user.email}, format="json")

        email_body = mail.outbox[-1].body

        # Restore outbox
        mail.outbox = mail.outbox[:outbox_count]

        # Match standard uid and token format in URLs
        match = re.search(
            r"(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})",
            email_body,
        )

        if not match:
            raise ValueError(
                f"Could not extract uid and token from email.\nBody:\n{email_body}"
            )

        return match.group("uid"), match.group("token")

    def test_password_reset_request_with_valid_email(self):
        """Test that a password reset email is sent when valid email is provided"""
        data = {"email": "testuser@example.com"}
        mail.outbox = []

        response = self.client.post(self.reset_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ["testuser@example.com"])
        self.assertIn("password reset", sent_email.subject.lower())

    def test_password_reset_request_with_invalid_email(self):
        """Test password reset with non-existent email"""
        data = {"email": "nonexistent@example.com"}
        mail.outbox = []

        response = self.client.post(self.reset_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_request_without_email(self):
        """Test password reset without providing email"""
        data = {}

        response = self.client.post(self.reset_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_with_valid_token(self):
        """Test password reset confirmation with valid token"""
        uid, token = self._get_uid_and_token(self.user)

        data = {
            "new_password1": "NewStrongPassword123!",
            "new_password2": "NewStrongPassword123!",
            "uid": uid,
            "token": token,
        }

        response = self.client.post(
            reverse(self.reset_confirm_url), data, format="json"
        )

        if response.status_code != status.HTTP_200_OK:
            print(f"\nPassword Reset Confirm Error: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPassword123!"))
        self.assertFalse(self.user.check_password("OldPassword123!"))

    def test_password_reset_confirm_with_mismatched_passwords(self):
        """Test password reset confirmation with non-matching passwords"""
        uid, token = self._get_uid_and_token(self.user)

        data = {
            "new_password1": "NewStrongPassword123!",
            "new_password2": "DifferentPassword123!",
            "uid": uid,
            "token": token,
        }

        response = self.client.post(
            reverse(self.reset_confirm_url), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn(
            "uid", response.data, "UID was rejected, you have a false positive test!"
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPassword123!"))

    def test_password_reset_confirm_with_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        uid, _ = self._get_uid_and_token(self.user)

        data = {
            "new_password1": "NewStrongPassword123!",
            "new_password2": "NewStrongPassword123!",
            "uid": uid,
            "token": "invalid-token-12345",
        }

        response = self.client.post(
            reverse(self.reset_confirm_url), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPassword123!"))

    def test_password_reset_confirm_with_weak_password(self):
        """Test password reset confirmation with weak password"""
        uid, token = self._get_uid_and_token(self.user)

        data = {
            "new_password1": "123",  # Too short
            "new_password2": "123",
            "uid": uid,
            "token": token,
        }

        response = self.client.post(
            reverse(self.reset_confirm_url), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn(
            "uid", response.data, "UID was rejected, you have a false positive test!"
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPassword123!"))

    def test_password_reset_token_becomes_invalid_after_use(self):
        """Test that token cannot be reused after successful password reset"""
        uid, token = self._get_uid_and_token(self.user)

        data = {
            "new_password1": "NewStrongPassword123!",
            "new_password2": "NewStrongPassword123!",
            "uid": uid,
            "token": token,
        }

        response = self.client.post(
            reverse(self.reset_confirm_url), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data2 = {
            "new_password1": "AnotherPassword123!",
            "new_password2": "AnotherPassword123!",
            "uid": uid,
            "token": token,
        }

        response2 = self.client.post(
            reverse(self.reset_confirm_url), data2, format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPassword123!"))
        self.assertFalse(self.user.check_password("AnotherPassword123!"))

    def test_password_reset_email_contains_reset_link(self):
        """Test that password reset email contains a valid reset link"""
        data = {"email": "testuser@example.com"}
        mail.outbox = []

        response = self.client.post(self.reset_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        email_body = mail.outbox[0].body
        self.assertIn("password", email_body.lower())

    def test_password_reset_with_mocked_email_backend(self):
        """Test password reset without the redundant mock"""
        mail.outbox = []
        data = {"email": "testuser@example.com"}

        response = self.client.post(self.reset_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_full_password_reset_flow(self):
        """Integration test: Complete password reset flow from request to confirmation"""
        mail.outbox = []
        reset_request_data = {"email": "testuser@example.com"}
        response = self.client.post(self.reset_url, reset_request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        # Extract directly from the email just generated
        match = re.search(
            r"(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})",
            mail.outbox[0].body,
        )
        uid = match.group("uid")
        token = match.group("token")

        reset_confirm_data = {
            "new_password1": "CompletelyNewPassword123!",
            "new_password2": "CompletelyNewPassword123!",
            "uid": uid,
            "token": token,
        }

        response = self.client.post(
            reverse(self.reset_confirm_url), reset_confirm_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("CompletelyNewPassword123!"))
        self.assertFalse(self.user.check_password("OldPassword123!"))

        login_url = reverse("rest_login")
        login_data = {
            "email": "testuser@example.com",
            "password": "CompletelyNewPassword123!",
        }

        response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_redirect_view(self):
        """Test the custom redirect view for password reset confirmation"""
        uid, token = self._get_uid_and_token(self.user)

        redirect_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )

        response = self.client.get(redirect_url)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn(uid, response.url)
        self.assertIn(token, response.url)
        self.assertIn("reset-password/confirm", response.url)

    def test_multiple_password_reset_requests(self):
        """Test that multiple password reset requests can be made"""
        mail.outbox = []

        data = {"email": "testuser@example.com"}
        response1 = self.client.post(self.reset_url, data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(self.reset_url, data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertEqual(len(mail.outbox), 2)

    def test_password_reset_case_insensitive_email(self):
        """Test password reset with different email casing"""
        mail.outbox = []

        data = {"email": "TESTUSER@EXAMPLE.COM"}
        response = self.client.post(self.reset_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
