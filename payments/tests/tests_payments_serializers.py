from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from payments.models import Payment
from payments.serializers import PaymentSerializer, PaymentNestedSerializer
from borrowings.models import Borrowing
from books.models import Book

User = get_user_model()


class PaymentSerializerTest(TestCase):
    def setUp(self):
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

    def test_payment_serializer(self):
        serializer = PaymentSerializer(self.payment)
        data = serializer.data
        self.assertEqual(data["status"], Payment.Status.PENDING)
        self.assertEqual(data["type"], Payment.Type.PAYMENT)
        self.assertEqual(data["borrowing"], self.borrowing.id)
        self.assertEqual(data["session_url"], "http://example.com/session")
        self.assertEqual(data["session_id"], "test_session_id")
        self.assertEqual(data["money_to_pay"], "70.00")

    def test_payment_nested_serializer(self):
        serializer = PaymentNestedSerializer(self.payment)
        data = serializer.data
        self.assertEqual(data["status"], Payment.Status.PENDING)
        self.assertEqual(data["type"], Payment.Type.PAYMENT)
        self.assertEqual(data["session_url"], "http://example.com/session")
        self.assertEqual(data["money_to_pay"], "70.00")

    def test_payment_serializer_read_only_fields(self):
        serializer = PaymentSerializer(self.payment)
        data = serializer.data
        self.assertIn("session_url", serializer.Meta.read_only_fields)
        self.assertIn("session_id", serializer.Meta.read_only_fields)
        self.assertIn("money_to_pay", serializer.Meta.read_only_fields)
        self.assertIn("borrowing", serializer.Meta.read_only_fields)
        self.assertIn("status", serializer.Meta.read_only_fields)
        self.assertIn("type", serializer.Meta.read_only_fields)
        self.assertIn("created_at", serializer.Meta.read_only_fields)
