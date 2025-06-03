from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from datetime import timedelta

from borrowings.models import Borrowing
from books.models import Book

User = get_user_model()


class BorrowingModelTest(TestCase):
    """Test suite for Borrowing model functionality and validation."""

    def setUp(self):
        """Set up test data for borrowing model tests."""
        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        # Create test book
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=10.00,
        )

        # Create test borrowing with valid dates
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )

    def test_borrowing_creation(self):
        """Test that a borrowing can be created with valid data."""
        self.assertEqual(self.borrowing.book, self.book)
        self.assertEqual(self.borrowing.user, self.user)
        self.assertEqual(self.borrowing.is_paid, False)
        self.assertIsNone(self.borrowing.actual_return_date)

    def test_borrowing_str_representation(self):
        """Test the string representation of a borrowing."""
        self.assertEqual(str(self.borrowing), self.book.title)

    def test_is_active_method(self):
        """Test the is_active method for both active and inactive borrowings."""
        # Test active borrowing
        self.assertEqual(self.borrowing.is_active(), "true")

        # Test inactive borrowing
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()
        self.assertEqual(self.borrowing.is_active(), "false")

    def test_validation_expected_return_date(self):
        """Test validation of expected return date with various scenarios."""
        # Test with past date
        with self.assertRaises(ValidationError) as context:
            Borrowing.objects.create(
                book=self.book,
                user=self.user,
                expected_return_date=timezone.now().date() - timedelta(days=1),
            )
        self.assertEqual(
            str(context.exception),
            "[ErrorDetail(string='The return date must be later than the borrowing date.', code='invalid')]",
        )

        # Test with current date
        with self.assertRaises(ValidationError) as context:
            Borrowing.objects.create(
                book=self.book,
                user=self.user,
                expected_return_date=timezone.now().date(),
            )
        self.assertEqual(
            str(context.exception),
            "[ErrorDetail(string='The return date must be later than the borrowing date.', code='invalid')]",
        )

    def test_borrowing_relationships(self):
        """Test relationships between Borrowing and related models (Book and User)."""
        # Test book relationship
        self.assertEqual(self.borrowing.book.borrowings.first(), self.borrowing)

        # Test user relationship
        self.assertEqual(self.borrowing.user.borrowings.first(), self.borrowing)

    def test_borrowing_default_values(self):
        """Test default values for borrowing fields on creation."""
        self.assertFalse(self.borrowing.is_paid)
        self.assertIsNone(self.borrowing.actual_return_date)
        self.assertEqual(self.borrowing.borrow_date, timezone.now().date())

    def test_borrowing_update(self):
        """Test updating borrowing fields after creation."""
        # Update actual return date
        return_date = timezone.now().date()
        self.borrowing.actual_return_date = return_date
        self.borrowing.save()
        self.assertEqual(self.borrowing.actual_return_date, return_date)

        # Update payment status
        self.borrowing.is_paid = True
        self.borrowing.save()
        self.assertTrue(self.borrowing.is_paid)
