from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing
from notifications.tasks import send_telegram_message
from notifications.signals import borrowing_created, book_created_or_updated

User = get_user_model()

class NotificationTasksTests(TestCase):
    @patch('notifications.tasks.bot.send_message')
    def test_send_telegram_message(self, mock_send_message):
        chat_id = 123456
        text = "Test message"
        
        # Mock the async send_message method
        mock_send_message.return_value = MagicMock()
        
        # Call the task
        send_telegram_message(chat_id, text)
        
        # Verify the message was sent with correct parameters
        mock_send_message.assert_called_once_with(chat_id=chat_id, text=text)

class NotificationSignalsTests(TestCase):
    def setUp(self):
        # Create test user with telegram chat ID
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            telegram_chat_id=123456
        )
        
        # Create test book
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="test.jpg",
            inventory=5,
            daily_fee=10.00
        )

    @patch('notifications.signals.send_telegram_message.delay')
    def test_borrowing_created_signal(self, mock_send_message):
        # Create a borrowing
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2024-03-20",
            expected_return_date="2024-04-20"
        )
        
        # Trigger the signal manually
        borrowing_created(Borrowing, borrowing, True)
        
        # Verify the message was sent
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertEqual(args[0], self.user.telegram_chat_id)
        self.assertIn(self.book.title, args[1])

    @patch('notifications.signals.send_telegram_message.delay')
    def test_book_created_signal(self, mock_send_message):
        # Create a new book
        new_book = Book.objects.create(
            title="New Book",
            author="New Author",
            cover="new.jpg",
            inventory=3,
            daily_fee=15.00
        )
        
        # Trigger the signal manually
        book_created_or_updated(Book, new_book, True)
        
        # Verify the message was sent
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertEqual(args[0], self.user.telegram_chat_id)
        self.assertIn(new_book.title, args[1])

    @patch('notifications.signals.send_telegram_message.delay')
    def test_book_updated_signal(self, mock_send_message):
        # Update the existing book
        self.book.title = "Updated Book"
        self.book.save()
        
        # Trigger the signal manually
        book_created_or_updated(Book, self.book, False)
        
        # Verify the message was sent
        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertEqual(args[0], self.user.telegram_chat_id)
        self.assertIn("Updated Book", args[1])
