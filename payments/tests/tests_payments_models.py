from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from payments.models import Payment
from borrowings.models import Borrowing
from books.models import Book

User = get_user_model()


class PaymentModelTest(TestCase):
    """Test suite for Payment model."""

    def setUp(self):
        """Set up test data for payment model tests."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            chat_id=123456,
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=10.00,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )
        self.payment = Payment.objects.create(
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
            borrowing=self.borrowing,
            session_url="http://example.com/session",
            session_id="test_session_id",
            money_to_pay=70.00,
        )

    def test_payment_creation(self):
        """Test payment object creation with all required fields."""
        self.assertEqual(self.payment.status, Payment.Status.PENDING)
        self.assertEqual(self.payment.type, Payment.Type.PAYMENT)
        self.assertEqual(self.payment.borrowing, self.borrowing)
        self.assertEqual(self.payment.session_url, "http://example.com/session")
        self.assertEqual(self.payment.session_id, "test_session_id")
        self.assertEqual(self.payment.money_to_pay, 70.00)

    def test_payment_str(self):
        """Test payment string representation format."""
        expected_str = f"{self.payment.type}, user: {self.borrowing.user.id}, book: {self.borrowing.book.title}"
        self.assertEqual(str(self.payment), expected_str)

    def test_payment_status_choices(self):
        """Test that payment status is one of the valid choices."""
        self.assertIn(
            self.payment.status, [status[0] for status in Payment.Status.choices]
        )

    def test_payment_type_choices(self):
        """Test that payment type is one of the valid choices."""
        self.assertIn(self.payment.type, [type[0] for type in Payment.Type.choices])
