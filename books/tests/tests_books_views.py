from django.urls import reverse
from rest_framework.test import APITestCase
from books.models import Book


class BookViewSetTest(APITestCase):
    def setUp(self):
        Book.objects.all().delete()
        self.book1 = Book.objects.create(
            title="Book One",
            author="Author One",
            cover="HARD",
            inventory=5,
            daily_fee="1.50",
        )
        self.book2 = Book.objects.create(
            title="Book Two",
            author="Author Two",
            cover="SOFT",
            inventory=3,
            daily_fee="2.00",
        )

    def test_list_books(self):
        url = reverse("books:book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_book(self):
        url = reverse("books:book-detail", args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.book1.title)

    def test_create_book(self):
        url = reverse("books:book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "3.00",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New Book")

    def test_update_book(self):
        url = reverse("books:book-detail", args=[self.book1.id])
        data = {
            "title": "Updated Book",
            "author": self.book1.author,
            "cover": self.book1.cover,
            "inventory": self.book1.inventory,
            "daily_fee": str(self.book1.daily_fee),
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Book")

    def test_partial_update_book(self):
        url = reverse("books:book-detail", args=[self.book2.id])
        data = {"inventory": 15}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["inventory"], 15)

    def test_delete_book(self):
        url = reverse("books:book-detail", args=[self.book2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Book.objects.filter(id=self.book2.id).exists())
