from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)

    def test_create_superuser(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_verified)

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="", password="testpass123")

    def test_create_superuser_without_staff_status(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="test@example.com",
                password="testpass123",
                is_staff=False
            )

    def test_create_superuser_without_superuser_status(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="test@example.com",
                password="testpass123",
                is_superuser=False
            )

    def test_user_str_representation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data["email"])

    def test_user_email_uniqueness(self):
        User.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)

    def test_user_password_validation(self):
        with self.assertRaises(ValidationError):
            User.objects.create_user(
                email="test@example.com",
                password="123"  # Too short password
            )

    def test_user_verification(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_verified)
        user.is_verified = True
        user.save()
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
