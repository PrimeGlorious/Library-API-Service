import asyncio
import logging
import os
from datetime import datetime, timedelta

from celery import shared_task
from aiogram import Bot
from dotenv import load_dotenv
from django.utils import timezone

from borrowings.models import Borrowing

load_dotenv()

logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))


@shared_task
def send_telegram_message(chat_id: int, text: str):
    async def send():
        await bot.send_message(chat_id=chat_id, text=text)

    try:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError
        except (RuntimeError, AssertionError):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(send())
    except Exception as e:
        logger.exception(f"Failed to send telegram message to chat_id={chat_id}")
        raise


@shared_task
def check_and_send_return_reminders():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    due_tomorrow = Borrowing.objects.filter(
        expected_return_date=tomorrow,
        actual_return_date__isnull=True,
        user__chat_id__isnull=False,
    ).select_related("user", "book")

    for borrowing in due_tomorrow:
        message = (
            f"📚 Reminder: Your book '{borrowing.book.title}' is due tomorrow!\n"
            f"Please return it to the library by {borrowing.expected_return_date}."
        )
        send_telegram_message.delay(borrowing.user.chat_id, message)

    overdue = Borrowing.objects.filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True,
        user__chat_id__isnull=False,
    ).select_related("user", "book")

    for borrowing in overdue:
        message = (
            f"⚠️ Overdue Notice: Your book '{borrowing.book.title}' is overdue!\n"
            f"It was due on {borrowing.expected_return_date}.\n"
            f"Please return it to the library as soon as possible."
        )
        send_telegram_message.delay(borrowing.user.chat_id, message)
