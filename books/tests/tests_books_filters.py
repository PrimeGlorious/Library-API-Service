from django.test import TestCase
from books.models import Book
from books.filters import BookFilter


class BookFilterTest(TestCase):
    def setUp(self):
        Book.objects.create(
            title="Python Programming",
            author="John Doe",
            cover=Book.CoverChoices.HARD,
            inventory=5,
            daily_fee=10.00,
        )
        Book.objects.create(
            title="Django for Beginners",
            author="Jane Smith",
            cover=Book.CoverChoices.SOFT,
            inventory=3,
            daily_fee=15.50,
        )
        Book.objects.create(
            title="Advanced Django",
            author="John Doe",
            cover=Book.CoverChoices.HARD,
            inventory=8,
            daily_fee=20.00,
        )

    def test_filter_by_title(self):
        f = BookFilter(data={"title": "django"})
        qs = f.qs
        self.assertEqual(qs.count(), 2)
        self.assertTrue(all("django" in book.title.lower() for book in qs))

    def test_filter_by_author(self):
        f = BookFilter(data={"author": "john"})
        qs = f.qs
        self.assertEqual(qs.count(), 2)
        self.assertTrue(all("john" in book.author.lower() for book in qs))

    def test_filter_by_cover(self):
        f = BookFilter(data={"cover": Book.CoverChoices.SOFT})
        qs = f.qs
        self.assertEqual(qs.count(), 1)
        self.assertTrue(all(book.cover == Book.CoverChoices.SOFT for book in qs))

    def test_filter_by_daily_fee_range(self):
        f = BookFilter(data={"daily_fee_min": 12, "daily_fee_max": 20})
        qs = f.qs
        self.assertEqual(qs.count(), 2)
        self.assertTrue(all(12 <= book.daily_fee <= 20 for book in qs))

    def test_filter_by_inventory_range(self):
        f = BookFilter(data={"inventory_min": 4, "inventory_max": 8})
        qs = f.qs
        self.assertEqual(qs.count(), 2)
        self.assertTrue(all(4 <= book.inventory <= 8 for book in qs))
