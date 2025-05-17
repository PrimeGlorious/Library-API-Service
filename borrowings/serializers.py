from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "expected_return_date",
        )

    def create(self, validated_data):
        book = validated_data.get("book")
        if book.inventory <= 0:
            raise ValidationError("This book is currently not available.")
        book.inventory -= 1
        book.save()
        return super().create(validated_data)


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.SlugRelatedField(
        source="book",
        read_only=True,
        slug_field="title",
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title"
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book"
        )


class BorrowingEmptySerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = []
