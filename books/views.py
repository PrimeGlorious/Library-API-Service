from django.shortcuts import render

from rest_framework import viewsets
from books.models import Book
from books.serializers import BookSerializer
from django_filters.rest_framework import DjangoFilterBackend
from books.filters import BookFilter


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter

    ordering_fields = ["title", "daily_fee", "inventory", "author"]
    ordering = ["title"]
