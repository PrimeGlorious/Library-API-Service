from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing
from notifications.tasks import send_telegram_message
from notifications.signals import borrowing_created, book_created_or_updated
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class NotificationTasksTests(TestCase):
    @patch("notifications.tasks.bot.send_message")
    def test_send_telegram_message(self, mock_send_message):
        chat_id = 123456
        text = "Test message"

        mock_send_message.return_value = MagicMock()

        send_telegram_message(chat_id, text)

        mock_send_message.assert_called_once_with(chat_id=chat_id, text=text)


class NotificationSignalsTests(TestCase):
    def setUp(self):

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

    @patch("notifications.signals.send_telegram_message.delay")
    def test_borrowing_created_signal(self, mock_send_message):
        # Create a borrowing
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )

        # Trigger the signal manually
        borrowing_created(Borrowing, borrowing, True)

        # Verify the message was sent
        self.assertEqual(mock_send_message.call_count, 4)
        calls = mock_send_message.call_args_list
        for call_args in calls:
            self.assertEqual(call_args[0][0], self.user.chat_id)
            self.assertIn(self.book.title, call_args[0][1])

    @patch("notifications.signals.send_telegram_message.delay")
    def test_book_created_signal(self, mock_send_message):

        new_book = Book.objects.create(
            title="New Book",
            author="New Author",
            cover="HARD",
            inventory=3,
            daily_fee=15.00,
        )

        # Trigger the signal manually
        book_created_or_updated(Book, new_book, True)

        self.assertEqual(mock_send_message.call_count, 2)
        args = mock_send_message.call_args[0]
        self.assertEqual(args[0], self.user.chat_id)
        self.assertIn(new_book.title, args[1])

    @patch("notifications.signals.send_telegram_message.delay")
    def test_book_updated_signal(self, mock_send_message):

        self.book.title = "Updated Book"
        self.book.save()

        book_created_or_updated(Book, self.book, False)

        self.assertEqual(mock_send_message.call_count, 2)
        args = mock_send_message.call_args[0]
        self.assertEqual(args[0], self.user.chat_id)
        self.assertIn("Updated Book", args[1])
