from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowings.models import Borrowing
from notifications.tasks import send_telegram_message

@receiver(post_save, sender=Borrowing)
def borrowing_created(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    if user.telegram_chat_id:
        text = (
            f"📚 New Borrowing:\n"
            f"Book: {instance.book.title}\n"
            f"Borrow date: {instance.borrow_date}\n"
            f"Expected return: {instance.expected_return_date}\n"
            f"Book ID: {instance.book.id}\n"
            f"User ID: {user.id}"
        )
        send_telegram_message.delay(user.telegram_chat_id, text)
