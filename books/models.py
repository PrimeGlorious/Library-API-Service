import os
import uuid
from django.db import models
from django.utils.text import slugify


def book_cover_image_filepath(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"
    return os.path.join("covers/", filename)


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD", "Hardcover"
        SOFT = "SOFT", "Softcover"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=5, choices=CoverChoices.choices)
    cover_image = models.ImageField(
        upload_to=book_cover_image_filepath,
        blank=True,
        null=True,
        verbose_name="Cover",
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} by {self.author}"
