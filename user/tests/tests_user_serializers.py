from django.test import TestCase
from django.contrib.auth import get_user_model
from user.serializers import UserSerializer, EmailVerificationSerializer, ResendVerificationSerializer
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserSerializerTest(TestCase):
    """Test suite for UserSerializer validation and functionality."""

    def setUp(self):
        """Set up test data for user serializer tests."""
        self.valid_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }

    def test_create_user_with_valid_data(self):
        """Test user creation with valid data."""
        serializer = UserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertTrue(user.check_password(self.valid_data["password"]))

    def test_create_user_with_mismatched_passwords(self):
        """Test user creation fails when passwords don't match."""
        invalid_data = self.valid_data.copy()
        invalid_data["password2"] = "differentpass"
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password2", serializer.errors)

    def test_create_user_with_short_password(self):
        """Test user creation fails with password shorter than minimum length."""
        invalid_data = self.valid_data.copy()
        invalid_data["password"] = "1234"
        invalid_data["password2"] = "1234"
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_update_user_password(self):
        """Test password update functionality for existing user."""
        user = User.objects.create_user(
            email="existing@example.com",
            password="oldpass123"
        )
        update_data = {
            "email": "existing@example.com",
            "password": "newpass123",
            "password2": "newpass123"
        }
        serializer = UserSerializer(user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertTrue(updated_user.check_password("newpass123"))


class EmailVerificationSerializerTest(TestCase):
    """Test suite for email verification token validation."""

    def setUp(self):
        """Set up test data for email verification tests."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        # Note: In real tests, this would be a proper JWT token
        self.valid_token = "valid_token"

    def test_validate_token_with_invalid_token(self):
        """Test validation fails with invalid token format."""
        serializer = EmailVerificationSerializer(data={"token": "invalid_token"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("token", serializer.errors)

    def test_validate_token_with_expired_token(self):
        """Test validation fails with expired token."""
        # Note: This test would need a proper expired JWT token
        serializer = EmailVerificationSerializer(data={"token": "expired_token"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("token", serializer.errors)


class ResendVerificationSerializerTest(TestCase):
    """Test suite for resend verification email functionality."""

    def setUp(self):
        """Set up test data for resend verification tests."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_validate_email_with_existing_user(self):
        """Test validation succeeds for existing unverified user."""
        serializer = ResendVerificationSerializer(data={"email": "test@example.com"})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")

    def test_validate_email_with_nonexistent_user(self):
        """Test validation fails for non-existent email."""
        serializer = ResendVerificationSerializer(data={"email": "nonexistent@example.com"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_validate_email_with_verified_user(self):
        """Test validation fails for already verified user."""
        self.user.is_verified = True
        self.user.save()
        serializer = ResendVerificationSerializer(data={"email": "test@example.com"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
