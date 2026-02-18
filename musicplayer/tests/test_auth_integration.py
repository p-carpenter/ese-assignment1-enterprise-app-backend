from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class CriticalAuthTests(APITestCase):
    def test_registration_and_login_flow(self):
        """
        Integration test: Can a user register, get a token, and then login?
        """
        register_url = reverse('rest_register')
        login_url = reverse('rest_login')
        
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'strong_password123',
            'password2': 'strong_password123'
        }

        # Try to Register
        response = self.client.post(register_url, user_data)
        
        if response.status_code != 201:
            print(f"\nREGISTRATION ERROR: {response.data}") 
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Registration failed")

        # Try to Login with those credentials
        login_data = {
            'email': 'new@example.com', 
            'password': 'strong_password123'
        }
        response = self.client.post(login_url, login_data)

        if response.status_code != 200:
            print(f"\nLOGIN ERROR: {response.data}") 
        # ----------------------------

        # 3. Verify we got a Token
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login failed")
        self.assertTrue('key' in response.data or 'access' in response.data, "No token returned")