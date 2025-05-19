from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.serializers import PaymentNestedSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "expected_return_date",
            "payments",
        )

    def create(self, validated_data):
        book = validated_data.get("book")

        if book.inventory <= 0:
            raise serializers.ValidationError("This book is currently not available.")

        book.inventory -= 1
        book.save()

        borrowing = super().create(validated_data)

        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Request context is required for payment creation")

        from payments.stripe_utils import create_stripe_payment_session
        create_stripe_payment_session(borrowing, request)

        return borrowing


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
