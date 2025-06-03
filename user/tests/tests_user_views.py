from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import jwt
from django.conf import settings

User = get_user_model()


class UserViewSetTest(TestCase):
    """Test suite for UserViewSet CRUD operations.
    
    This test suite covers:
    - User creation with validation
    - User retrieval
    - User update
    - User deletion
    - Authentication requirements
    """

    def setUp(self):
        """Set up test data including regular and admin users."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True
        )

    def test_create_user(self):
        """Test creating a new user with valid data.
        
        Verifies:
        - User is created successfully
        - Response has correct status code
        - User exists in database
        """
        url = reverse("user:user-list")
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password2": "newpass123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_create_user_with_mismatched_passwords(self):
        """Test user creation fails when passwords don't match.
        
        Verifies:
        - Request is rejected
        - User is not created
        - Response has correct error status
        """
        url = reverse("user:user-list")
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password2": "differentpass"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_retrieve_user(self):
        """Test retrieving user details.
        
        Verifies:
        - Authenticated user can retrieve their details
        - Response contains correct user data
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("user:user-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_user(self):
        """Test updating user details.
        
        Verifies:
        - User can update their email and password
        - Changes are saved correctly
        - Response has correct status code
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("user:user-detail", args=[self.user.id])
        data = {
            "email": "updated@example.com",
            "password": "updatedpass123",
            "password2": "updatedpass123"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertTrue(self.user.check_password("updatedpass123"))

    def test_delete_user(self):
        """Test user deletion.
        
        Verifies:
        - User can delete their account
        - Account is removed from database
        - Response has correct status code
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("user:user-detail", args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)


class EmailVerificationViewTest(TestCase):
    """Test suite for email verification functionality.
    
    This test suite covers:
    - Email verification with valid token
    - Email verification with invalid token
    - User verification status updates
    """

    def setUp(self):
        """Set up test data including user and verification token."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.token = jwt.encode(
            {"user_id": self.user.id},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

    def test_verify_email_with_valid_token(self):
        """Test email verification with valid token.
        
        Verifies:
        - Verification succeeds
        - User is marked as verified
        - Response has correct status code
        """
        url = reverse("user:verify-email")
        data = {"token": self.token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_verify_email_with_invalid_token(self):
        """Test email verification with invalid token.
        
        Verifies:
        - Verification fails
        - User remains unverified
        - Response has correct error status
        """
        url = reverse("user:verify-email")
        data = {"token": "invalid_token"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)


class ResendVerificationViewTest(TestCase):
    """Test suite for resend verification email functionality.
    
    This test suite covers:
    - Resending verification to valid unverified user
    - Attempting to resend to non-existent user
    - Attempting to resend to already verified user
    """

    def setUp(self):
        """Set up test data including unverified user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_resend_verification_with_valid_email(self):
        """Test resending verification to valid unverified user.
        
        Verifies:
        - Request succeeds
        - Response has correct status code
        """
        url = reverse("user:resend-verification")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resend_verification_with_nonexistent_email(self):
        """Test resending verification to non-existent user.
        
        Verifies:
        - Request fails
        - Response has correct error status
        """
        url = reverse("user:resend-verification")
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_verification_with_verified_user(self):
        """Test resending verification to already verified user.
        
        Verifies:
        - Request fails
        - Response has correct error status
        """
        self.user.is_verified = True
        self.user.save()
        url = reverse("user:resend-verification")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
