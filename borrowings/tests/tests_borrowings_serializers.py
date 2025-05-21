from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from datetime import timedelta

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingEmptySerializer,
)
from books.models import Book
from books.serializers import BookSerializer

User = get_user_model()


class BorrowingSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.get("/")

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

        # Create test borrowing
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )

    def test_borrowing_serializer_fields(self):
        """Test BorrowingSerializer fields"""
        serializer = BorrowingSerializer(
            self.borrowing, context={"request": self.request}
        )
        data = serializer.data

        self.assertEqual(
            set(data.keys()), {"id", "book", "expected_return_date", "payments"}
        )
        self.assertEqual(data["book"], self.book.id)
        self.assertEqual(
            data["expected_return_date"],
            self.borrowing.expected_return_date.isoformat(),
        )

    def test_borrowing_serializer_create_with_no_inventory(self):
        """Test BorrowingSerializer create with no inventory"""
        self.book.inventory = 0
        self.book.save()

        serializer = BorrowingSerializer(
            data={
                "book": self.book.id,
                "user": self.user.id,
                "expected_return_date": (
                    timezone.now().date() + timedelta(days=7)
                ).isoformat(),
            },
            context={"request": self.request},
        )

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
            serializer.save()

        self.assertIn("This book is currently not available", str(context.exception))

    def test_borrowing_serializer_create_without_request(self):
        """Test BorrowingSerializer create without request context"""
        serializer = BorrowingSerializer(
            data={
                "book": self.book.id,
                "user": self.user.id,
                "expected_return_date": (
                    timezone.now().date() + timedelta(days=7)
                ).isoformat(),
            }
        )

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn(
            "Request context is required for payment creation", str(context.exception)
        )

    def test_borrowing_list_serializer(self):
        """Test BorrowingListSerializer"""
        serializer = BorrowingListSerializer(self.borrowing)
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "borrow_date",
                "expected_return_date",
                "actual_return_date",
                "book_title",
            },
        )
        self.assertEqual(data["book_title"], self.book.title)

    def test_borrowing_detail_serializer(self):
        """Test BorrowingDetailSerializer"""
        serializer = BorrowingDetailSerializer(self.borrowing)
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            {"id", "borrow_date", "expected_return_date", "actual_return_date", "book"},
        )
        self.assertIsInstance(data["book"], dict)
        self.assertEqual(data["book"]["title"], self.book.title)

    def test_borrowing_empty_serializer(self):
        """Test BorrowingEmptySerializer"""
        serializer = BorrowingEmptySerializer(self.borrowing)
        data = serializer.data

        self.assertEqual(data, {})
