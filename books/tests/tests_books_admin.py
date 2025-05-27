from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse
from books.admin import BookAdmin
from books.models import Book

User = get_user_model()


class BookAdminTest(TestCase):
    """Test suite for BookAdmin configuration and functionality."""

    def setUp(self):
        """Set up test environment with admin site and superuser."""
        self.admin_site = AdminSite()
        self.book_admin = BookAdmin(Book, self.admin_site)
        # Create and login superuser for admin access
        self.user = User.objects.create_superuser(
            email="admin@example.com", password="password"
        )
        self.client.login(email="admin@example.com", password="password")

    def test_list_display(self):
        """Test that BookAdmin displays all required fields in list view."""
        expected_list_display = [
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
            "cover_image",
        ]
        self.assertEqual(list(self.book_admin.list_display), expected_list_display)

    def test_admin_view(self):
        """Test that book admin list view is accessible."""
        url = reverse("admin:books_book_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
