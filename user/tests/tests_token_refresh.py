from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

class TokenRefreshEndpointTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpassword123"
        )
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.url = reverse("user:token_refresh")

    def test_token_refresh_success(self):
        data = {"refresh": self.refresh_token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token(self):
        data = {"refresh": "invalid_token"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)