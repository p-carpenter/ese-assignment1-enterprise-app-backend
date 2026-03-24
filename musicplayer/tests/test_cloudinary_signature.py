from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import override_settings
import cloudinary.utils

User = get_user_model()


@override_settings(CLOUDINARY_API_SECRET="testsecret", CLOUDINARY_API_KEY="testkey")
class CloudinarySignatureTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pw")

    def test_authenticated_get_returns_signature_and_timestamp(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/cloudinary/generate-signature/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # Basic keys present
        self.assertIn("signature", data)
        self.assertIn("timestamp", data)
        self.assertIn("api_key", data)
        self.assertEqual(data["api_key"], "testkey")

        # Recompute signature using the returned timestamp to ensure correctness
        returned_ts = data["timestamp"]
        params = {"timestamp": returned_ts, "folder": "prod"}
        expected_sig = cloudinary.utils.api_sign_request(params, "testsecret")
        self.assertEqual(data["signature"], expected_sig)

    def test_unauthenticated_get_returns_401(self):
        response = self.client.get("/api/cloudinary/generate-signature/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
