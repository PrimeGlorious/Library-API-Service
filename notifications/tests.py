from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from notifications.tasks import send_telegram_message, check_and_send_return_reminders
from borrowings.models import Borrowing
from user.models import User
from books.models import Book


class NotificationTasksTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@user.ua", password="testpass123", chat_id=123456789
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", daily_fee=1, inventory=1
        )

    @patch("notifications.tasks.bot.send_message")
    def test_send_telegram_message(self, mock_send_message):
        chat_id = 123456789
        message = "Test message"
        send_telegram_message(chat_id, message)
        mock_send_message.assert_called_once_with(chat_id=chat_id, text=message)

    @patch("notifications.tasks.send_telegram_message.delay")
    def test_check_due_tomorrow_notifications(self, mock_send):
        tomorrow = timezone.now().date() + timedelta(days=1)
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=tomorrow,
        )
        mock_send.reset_mock()
        check_and_send_return_reminders()
        expected_message = (
            f"📚 Reminder: Your book '{self.book.title}' is due tomorrow!\n"
            f"Please return it to the library by {tomorrow}."
        )
        mock_send.assert_called_once_with(self.user.chat_id, expected_message)

    @patch("notifications.tasks.send_telegram_message.delay")
    def test_check_overdue_notifications(self, mock_send):
        yesterday = timezone.now().date() - timedelta(days=1)
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timedelta(days=1),
        )
        Borrowing.objects.filter(id=borrowing.id).update(
            borrow_date=timezone.now().date() - timedelta(days=2),
            expected_return_date=timezone.now().date() - timedelta(days=1),
        )
        mock_send.reset_mock()
        check_and_send_return_reminders()
        expected_message = (
            f"⚠️ Overdue Notice: Your book '{self.book.title}' is overdue!\n"
            f"It was due on {yesterday}.\n"
            f"Please return it to the library as soon as possible."
        )
        mock_send.assert_called_once_with(self.user.chat_id, expected_message)

    @patch("notifications.tasks.send_telegram_message.delay")
    def test_no_notification_for_returned_books(self, mock_send):
        with patch("notifications.tasks.send_telegram_message.delay"):
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                expected_return_date=timezone.now().date() + timedelta(days=1),
                actual_return_date=timezone.now(),
            )
        mock_send.reset_mock()
        check_and_send_return_reminders()
        mock_send.assert_not_called()
