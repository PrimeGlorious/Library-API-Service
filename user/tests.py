from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta, datetime
import jwt
from django.conf import settings
import time

User = get_user_model()


class UserManagerTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        """Test creating a regular user"""
        user = self.User.objects.create_user(
            email="normal@user.com", password="testpass123"
        )
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)

        # Test that password was set correctly
        self.assertTrue(user.check_password("testpass123"))

    def test_create_user_without_email(self):
        """Test creating a user without email raises error"""
        with self.assertRaises(ValueError):
            self.User.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = self.User.objects.create_superuser(
            email="admin@user.com", password="testpass123"
        )
        self.assertEqual(admin_user.email, "admin@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertIsNone(admin_user.username)

    def test_create_superuser_with_invalid_flags(self):
        """Test creating superuser with invalid is_staff or is_superuser flags"""
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email="admin@user.com", password="testpass123", is_staff=False
            )

        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email="admin@user.com", password="testpass123", is_superuser=False
            )

    def test_email_normalize(self):
        """Test email is normalized when creating a user"""
        email = "test@EXAMPLE.com"
        user = self.User.objects.create_user(email=email, password="testpass123")
        self.assertEqual(user.email, email.lower())


class SignUpAndVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse("user:signup")
        self.verify_url = reverse("user:email-verify")

        # Test user data
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }

    def test_successful_user_registration(self):
        """Test successful user registration"""
        response = self.client.post(self.signup_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user_data", response.data)
        self.assertEqual(response.data["user_data"]["email"], self.user_data["email"])

        # Check user was created
        user = User.objects.get(email=self.user_data["email"])
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password(self.user_data["password"]))

    def test_registration_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        data = self.user_data.copy()
        data["password2"] = "different_password"

        response = self.client.post(self.signup_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data)
        self.assertEqual(response.data["password2"][0], "Password don`t match.")

    def test_registration_with_short_password(self):
        """Test registration with password shorter than 5 characters"""
        data = self.user_data.copy()
        data["password"] = "1234"
        data["password2"] = "1234"

        response = self.client.post(self.signup_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_with_invalid_email(self):
        """Test registration with invalid email format"""
        data = self.user_data.copy()
        data["email"] = "invalid_email"

        response = self.client.post(self.signup_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_email_verification_with_valid_token(self):
        """Test email verification with valid token"""
        # First register a user
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the user and create verification token
        user = User.objects.get(email=self.user_data["email"])
        token = RefreshToken.for_user(user).access_token

        # Verify email
        response = self.client.get(f"{self.verify_url}?token={token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "Successfully activated")

        # Check user is verified
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_email_verification_with_invalid_token(self):
        """Test email verification with invalid token"""
        response = self.client.get(f"{self.verify_url}?token=invalid_token")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token")

    def test_email_verification_with_expired_token(self):
        """Test email verification with expired token"""
        # First register a user
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the user and create expired token
        user = User.objects.get(email=self.user_data["email"])

        # Create a token that expired 1 minute ago
        payload = {
            "user_id": user.id,
            "exp": int(time.time()) - 60,  # Expired 1 minute ago
            "iat": int(time.time()) - 600,  # Created 10 minutes ago
        }
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # Try to verify with expired token
        response = self.client.get(f"{self.verify_url}?token={expired_token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Activation Expired")

    def test_email_verification_without_token(self):
        """Test email verification without providing token"""
        response = self.client.get(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token")

    def test_verification_of_already_verified_user(self):
        """Test verification of already verified user"""
        # First register a user
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the user and verify them
        user = User.objects.get(email=self.user_data["email"])
        user.is_verified = True
        user.save()

        # Create verification token
        token = RefreshToken.for_user(user).access_token

        # Try to verify again
        response = self.client.get(f"{self.verify_url}?token={token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "Successfully activated")

        # Check user is still verified
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_resend_verification_email(self):
        """Test resending verification email to unverified user"""
        # First register a user
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Request resend verification email
        resend_url = reverse("user:resend-verification")
        response = self.client.post(resend_url, {"email": self.user_data["email"]})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Verification email has been resent")

    def test_resend_verification_email_to_nonexistent_user(self):
        """Test resending verification email to non-existent user"""
        resend_url = reverse("user:resend-verification")
        response = self.client.post(resend_url, {"email": "nonexistent@example.com"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User with this email does not exist")

    def test_resend_verification_email_to_verified_user(self):
        """Test resending verification email to already verified user"""
        # First register a user
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the user
        user = User.objects.get(email=self.user_data["email"])
        user.is_verified = True
        user.save()

        # Request resend verification email
        resend_url = reverse("user:resend-verification")
        response = self.client.post(resend_url, {"email": self.user_data["email"]})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User is already verified")

    def test_resend_verification_email_without_email(self):
        """Test resending verification email without providing email"""
        resend_url = reverse("user:resend-verification")
        response = self.client.post(resend_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data['error'], 'Email is required')


class TokenEndpointsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.token_url = reverse("user:token_obtain_pair")
        self.token_refresh_url = reverse("user:token_refresh")
        self.token_verify_url = reverse("user:token_verify")

    def test_token_obtain_pair_success(self):
        """Test obtaining access and refresh tokens with valid credentials"""
        response = self.client.post(
            self.token_url, {"email": self.user.email, "password": "testpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_obtain_pair_invalid_credentials(self):
        """Test obtaining tokens with invalid credentials"""
        response = self.client.post(
            self.token_url, {"email": self.user.email, "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_refresh_success(self):
        """Test refreshing access token with a valid refresh token"""
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(self.token_refresh_url, {"refresh": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token(self):
        """Test refreshing access token with an invalid refresh token"""
        response = self.client.post(self.token_refresh_url, {"refresh": "invalidtoken"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_verify_success(self):
        """Test verifying a valid access token"""
        access = RefreshToken.for_user(self.user).access_token
        response = self.client.post(self.token_verify_url, {"token": str(access)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid_token(self):
        """Test verifying an invalid access token"""
        response = self.client.post(self.token_verify_url, {"token": "invalidtoken"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

        self.assertEqual(response.data["error"], "Email is required")
