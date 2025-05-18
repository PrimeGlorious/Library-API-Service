from django.test import TestCase
from django.contrib.auth import get_user_model


class UserManagerTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        """Test creating a regular user"""
        user = self.User.objects.create_user(
            email='normal@user.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)
        
        # Test that password was set correctly
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_without_email(self):
        """Test creating a user without email raises error"""
        with self.assertRaises(ValueError):
            self.User.objects.create_user(email='', password='testpass123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = self.User.objects.create_superuser(
            email='admin@user.com',
            password='testpass123'
        )
        self.assertEqual(admin_user.email, 'admin@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertIsNone(admin_user.username)

    def test_create_superuser_with_invalid_flags(self):
        """Test creating superuser with invalid is_staff or is_superuser flags"""
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email='admin@user.com',
                password='testpass123',
                is_staff=False
            )
        
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email='admin@user.com',
                password='testpass123',
                is_superuser=False
            )

    def test_email_normalize(self):
        """Test email is normalized when creating a user"""
        email = 'test@EXAMPLE.com'
        user = self.User.objects.create_user(email=email, password='testpass123')
        self.assertEqual(user.email, email.lower())
