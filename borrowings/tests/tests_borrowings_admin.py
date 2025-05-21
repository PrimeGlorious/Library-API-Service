from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from borrowings.admin import BorrowingAdmin
from borrowings.models import Borrowing
from books.models import Book

User = get_user_model()


class MockRequest:
    pass


class BorrowingAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = BorrowingAdmin(Borrowing, self.site)

        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=10.00,
        )

        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )

    def test_list_display(self):
        """Test that list_display contains all required fields"""
        self.assertEqual(
            self.admin.list_display,
            (
                "book",
                "user",
                "borrow_date",
                "expected_return_date",
                "actual_return_date",
                "is_paid",
            ),
        )

    def test_list_filter(self):
        """Test that list_filter contains all required fields"""
        self.assertEqual(
            self.admin.list_filter,
            (
                "is_paid",
                "borrow_date",
                "expected_return_date",
                "actual_return_date",
            ),
        )

    def test_search_fields(self):
        """Test that search_fields contains all required fields"""
        self.assertEqual(
            self.admin.search_fields, ("book__title", "user__email")
        )

    def test_ordering(self):
        """Test that ordering is set correctly"""
        self.assertEqual(self.admin.ordering, ("-borrow_date",))

    def test_admin_str_representation(self):
        """Test the string representation in admin"""
        self.assertEqual(str(self.borrowing), self.book.title)

    def test_is_active_method(self):
        """Test the is_active method"""
        self.assertEqual(self.borrowing.is_active(), "true")

        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()
        self.assertEqual(self.borrowing.is_active(), "false")
