import asyncio
import os
from datetime import datetime, timedelta

from celery import shared_task
from aiogram import Bot
from dotenv import load_dotenv
from django.utils import timezone

from borrowings.models import Borrowing

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))


@shared_task
def send_telegram_message(chat_id: int, text: str):
    try:
        async def send():
            await bot.send_message(chat_id=chat_id, text=text)

        asyncio.run(send())
    except Exception as e:
        print(f"Failed to send telegram message: {e}")
        raise


@shared_task
def check_and_send_return_reminders():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    # Get borrowings that are due tomorrow
    due_tomorrow = Borrowing.objects.filter(
        expected_return_date=tomorrow,
        actual_return_date__isnull=True,
        user__chat_id__isnull=False
    ).select_related('user', 'book')

    for borrowing in due_tomorrow:
        message = (
            f"📚 Reminder: Your book '{borrowing.book.title}' is due tomorrow!\n"
            f"Please return it to the library by {borrowing.expected_return_date}."
        )
        send_telegram_message.delay(borrowing.user.chat_id, message)

    # Get overdue borrowings
    overdue = Borrowing.objects.filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True,
        user__chat_id__isnull=False
    ).select_related('user', 'book')

    for borrowing in overdue:
        message = (
            f"⚠️ Overdue Notice: Your book '{borrowing.book.title}' is overdue!\n"
            f"It was due on {borrowing.expected_return_date}.\n"
            f"Please return it to the library as soon as possible."
        )
        send_telegram_message.delay(borrowing.user.chat_id, message)