from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from unittest.mock import patch

from borrowings.models import Borrowing
from books.models import Book

User = get_user_model()


class BorrowingsViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create regular user
        self.user = User.objects.create_user(
            email="user@example.com", password="userpass123"
        )

        # Create admin user
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )

        # Create test book
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=10.00,
        )

        # Create test borrowing for regular user
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=timezone.now().date() + timedelta(days=7),
            is_paid=True,
        )

    def test_list_borrowings_unauthorized(self):
        """Test that unauthorized users cannot list borrowings"""
        url = reverse("borrowings:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_borrowings_authorized(self):
        """Test that authorized users can list their borrowings"""
        self.client.force_authenticate(user=self.user)
        url = reverse("borrowings:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # Only user's borrowing

    def test_retrieve_own_borrowing(self):
        """Test that users can retrieve their own borrowings"""
        self.client.force_authenticate(user=self.user)
        url = reverse("borrowings:borrowing-detail", args=[self.borrowing.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)

    @patch("payments.stripe_utils.stripe.checkout.Session.create")
    def test_create_borrowing(self, mock_stripe):
        """Test creating a new borrowing"""
        # Mock Stripe response
        mock_stripe.return_value = type(
            "obj", (object,), {"url": "http://test.com", "id": "test_session_id"}
        )

        self.client.force_authenticate(user=self.user)
        url = reverse("borrowings:borrowing-list")
        data = {
            "book": self.book.id,
            "expected_return_date": (
                timezone.now().date() + timedelta(days=7)
            ).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 2)

    def test_book_return_own(self):
        """Test that users can return their own books"""
        self.client.force_authenticate(user=self.user)
        url = reverse("borrowings:borrowing-book-return", args=[self.borrowing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that book inventory increased
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

        # Check that borrowing was marked as returned
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)

    def test_filter_borrowings_by_active(self):
        """Test filtering borrowings by active status"""
        self.client.force_authenticate(user=self.user)
        url = reverse("borrowings:borrowing-list")

        # Test active borrowings
        response = self.client.get(f"{url}?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Test inactive borrowings
        self.borrowing.actual_return_date = timezone.now()
        self.borrowing.save()
        response = self.client.get(f"{url}?is_active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
