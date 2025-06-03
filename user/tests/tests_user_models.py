from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserModelTest(TestCase):
    """Test suite for User model functionality and validation.
    
    This test suite covers:
    - User creation (regular and superuser)
    - User validation rules
    - User field constraints
    - User verification status
    """

    def setUp(self):
        """Set up test data for user model tests."""
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }

    def test_create_user(self):
        """Test creation of a regular user with valid data.
        
        Verifies:
        - Email is set correctly
        - Password is hashed and can be verified
        - Default flags are set correctly (not staff, not superuser, not verified)
        """
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)

    def test_create_superuser(self):
        """Test creation of a superuser with valid data.
        
        Verifies:
        - Email is set correctly
        - Password is hashed and can be verified
        - Superuser flags are set correctly (staff, superuser, verified)
        """
        user = User.objects.create_superuser(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_verified)

    def test_create_user_without_email(self):
        """Test that user creation fails when email is empty."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser_without_email(self):
        """Test that superuser creation fails when email is empty."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="", password="testpass123")

    def test_create_superuser_without_staff_status(self):
        """Test that superuser creation fails when is_staff is False."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="test@example.com",
                password="testpass123",
                is_staff=False
            )

    def test_create_superuser_without_superuser_status(self):
        """Test that superuser creation fails when is_superuser is False."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="test@example.com",
                password="testpass123",
                is_superuser=False
            )

    def test_user_str_representation(self):
        """Test that user's string representation is their email address."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data["email"])

    def test_user_email_uniqueness(self):
        """Test that users cannot be created with duplicate email addresses."""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)

    def test_user_password_validation(self):
        """Test that password validation prevents weak passwords."""
        with self.assertRaises(ValidationError):
            User.objects.create_user(
                email="test@example.com",
                password="123"  # Too short password
            )

    def test_user_verification(self):
        """Test user verification status can be updated.
        
        Verifies:
        - New users start as unverified
        - Verification status can be updated
        - Changes persist after saving
        """
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_verified)
        user.is_verified = True
        user.save()
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
