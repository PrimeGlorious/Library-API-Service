from django.test import TestCase
from books.models import Book
from books.serializers import BookSerializer


class BookSerializerTest(TestCase):
    """Test suite for BookSerializer validation and serialization."""

    def setUp(self):
        """Set up test data for book serializer tests."""
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee="3.99",
        )

    def test_valid_data(self):
        """Test serializer validation with valid data."""
        valid_data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 10,
            "daily_fee": "2.50",
        }
        serializer = BookSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_cover_choice(self):
        """Test serializer validation fails with invalid cover type."""
        invalid_data = {
            "title": "Invalid Book",
            "author": "Author",
            "cover": "PB",  # Invalid cover type
            "inventory": 10,
            "daily_fee": "2.50",
        }
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("cover", serializer.errors)
        self.assertEqual(serializer.errors["cover"][0].code, "invalid_choice")

    def test_serialization(self):
        """Test that serializer correctly serializes book data."""
        serializer = BookSerializer(self.book)
        data = serializer.data
        self.assertEqual(data["title"], self.book.title)
        self.assertEqual(data["author"], self.book.author)
        self.assertEqual(data["cover"], self.book.cover)
        self.assertEqual(data["inventory"], self.book.inventory)
        self.assertEqual(str(data["daily_fee"]), str(self.book.daily_fee))
