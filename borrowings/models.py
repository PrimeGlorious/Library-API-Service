from django.conf import settings
from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import (
    ValidationError
)

from books.models import Book


class Borrowing(models.Model):
    book = models.ForeignKey(
        to=Book,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    def clean(self):
        super().clean()
        borrow_date = now().date()
        expected_return_date = self.expected_return_date

        if borrow_date >= expected_return_date:
            raise ValidationError("The return date must be later than the borrowing date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def is_active(self):
        return "true" if self.actual_return_date is None else "false"

    def __str__(self):
        return self.book.title
