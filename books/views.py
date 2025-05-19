from django.shortcuts import render

from rest_framework import viewsets
from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from books.filters import BookFilter


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BookFilter

    ordering_fields = ["title", "daily_fee", "inventory", "author"]
    ordering = ["title"]
