from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import now, timedelta

from books.models import Book
from borrowings.models import Borrowing


class BorrowingViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="pass123"
        )
        self.other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="pass456"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=3,
            daily_fee=2
        )

        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=now().date() + timedelta(days=7)
        )

    def authenticate(self, user=None):
        if not user:
            user = self.user
        self.client.force_authenticate(user=user)

    def test_list_user_borrowings(self):
        self.authenticate()
        url = reverse("borrowings:borrowing-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_borrowings_is_active_true(self):
        self.authenticate()
        url = reverse("borrowings:borrowing-list") + "?is_active=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_borrowings_is_active_false(self):
        self.authenticate()
        self.borrowing.actual_return_date = now().date()
        self.borrowing.save()
        url = reverse("borrowings:borrowing-list") + "?is_active=false"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_own_borrowing(self):
        self.authenticate()
        url = reverse(
            "borrowings:borrowing-detail",
            args=[self.borrowing.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)

    def test_retrieve_other_user_borrowing_forbidden(self):
        self.authenticate(self.other_user)
        url = reverse(
            "borrowings:borrowing-detail",
            args=[self.borrowing.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_borrowing_success(self):
        self.authenticate()
        url = reverse("borrowings:borrowing-list")
        data = {
            "book": self.book.id,
            "expected_return_date": (now().date() + timedelta(days=5)).isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

    def test_create_borrowing_no_inventory(self):
        self.book.inventory = 0
        self.book.save()
        self.authenticate()
        url = reverse("borrowings:borrowing-list")
        data = {
            "book": self.book.id,
            "expected_return_date": (now().date() + timedelta(days=5)).isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book_success(self):
        self.authenticate()
        url = reverse(
            "borrowings:borrowing-book-return",
            args=[self.borrowing.id]
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_return_book_already_returned(self):
        self.borrowing.actual_return_date = now()
        self.borrowing.save()
        self.authenticate()
        url = reverse(
            "borrowings:borrowing-book-return",
            args=[self.borrowing.id]
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book_not_owner(self):
        self.authenticate(self.other_user)
        url = reverse(
            "borrowings:borrowing-book-return",
            args=[self.borrowing.id]
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
