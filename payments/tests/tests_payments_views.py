from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import json

from payments.models import Payment
from borrowings.models import Borrowing
from books.models import Book

User = get_user_model()


class PaymentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            chat_id=123456,
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
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

    def test_payment_list_for_staff(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("payments:payment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_payment_list_for_non_staff(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("payments:payment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_payment_list_for_unauthorized(self):
        url = reverse("payments:payment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StripeWebhookViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
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

    def test_stripe_webhook_invalid_payload(self):
        url = reverse("payments:stripe-webhook")
        payload = {"type": "invalid"}
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_signature",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PaymentCancelViewTest(TestCase):
    def test_payment_cancel(self):
        url = reverse("payments:cancel")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            "Payment was cancelled. You can pay later within 24 hours.",
        )
