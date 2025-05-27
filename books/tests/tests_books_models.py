from django.test import TestCase
from books.models import Book


class BookModelTest(TestCase):
    """Test suite for Book model functionality."""

    def setUp(self):
        """Set up test data for book model tests."""
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverChoices.HARD,
            inventory=10,
            daily_fee=1.99,
        )

    def test_str_method(self):
        """Test string representation of Book model."""
        self.assertEqual(str(self.book), "Test Book by Test Author")

    def test_book_fields(self):
        """Test that all book fields are correctly set and retrieved."""
        book = self.book
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.cover, Book.CoverChoices.HARD)
        self.assertEqual(book.inventory, 10)
        self.assertEqual(float(book.daily_fee), 1.99)

    def test_cover_choices(self):
        """Test that book cover type is one of the valid choices."""
        choices = dict(Book.CoverChoices.choices)
        self.assertIn(self.book.cover, choices.keys())
        self.assertEqual(choices[self.book.cover], "Hardcover")
