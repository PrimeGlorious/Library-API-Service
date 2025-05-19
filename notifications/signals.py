from django.db.models.signals import post_save
from django.dispatch import receiver
from books.models import Book
from borrowings.models import Borrowing
from notifications.tasks import send_telegram_message
from user.models import User


@receiver(post_save, sender=Borrowing)
def borrowing_created(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    if user.chat_id:
        text = (
            f"📚 New Borrowing:\n"
            f"Book: {instance.book.title}\n"
            f"Borrow date: {instance.borrow_date}\n"
            f"Expected return: {instance.expected_return_date}\n"
            f"Book ID: {instance.book.id}\n"
            f"User ID: {user.id}"
        )
        send_telegram_message.delay(user.chat_id, text)
        for user in User.objects.exclude(chat_id__isnull=True):
            send_telegram_message.delay(user.chat_id, text)


@receiver(post_save, sender=Book)
def book_created_or_updated(sender, instance, created, **kwargs):
    if created:
        text = (
            f"📚 New Book Added:\n"
            f"Title: {instance.title}\n"
            f"Author: {instance.author}\n"
            f"Cover: {instance.cover}\n"
            f"Inventory: {instance.inventory}\n"
            f"Daily Fee: ${instance.daily_fee}"
        )
    else:
        text = (
            f"✏️ Book Updated:\n"
            f"Title: {instance.title}\n"
            f"Author: {instance.author}\n"
            f"Cover: {instance.cover}\n"
            f"Inventory: {instance.inventory}\n"
            f"Daily Fee: ${instance.daily_fee}"
        )

    for user in User.objects.exclude(chat_id__isnull=True):
        send_telegram_message.delay(user.chat_id, text)