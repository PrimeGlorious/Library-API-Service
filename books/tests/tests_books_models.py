from django.test import TestCase
from books.models import Book


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverChoices.HARD,
            inventory=10,
            daily_fee=1.99,
        )

    def test_str_method(self):
        self.assertEqual(str(self.book), "Test Book by Test Author")

    def test_book_fields(self):
        book = self.book
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.cover, Book.CoverChoices.HARD)
        self.assertEqual(book.inventory, 10)
        self.assertEqual(float(book.daily_fee), 1.99)

    def test_cover_choices(self):
        choices = dict(Book.CoverChoices.choices)
        self.assertIn(self.book.cover, choices.keys())
        self.assertEqual(choices[self.book.cover], "Hardcover")
