from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingSerializer, BorrowingListSerializer, BorrowingEmptySerializer
)


class BorrowingsViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Borrowing.objects.all().order_by("-borrow_date")
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset.filter(
            user=self.request.user,
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        elif self.action == "book_return":
            return BorrowingEmptySerializer
        return BorrowingSerializer

    @action(detail=True, methods=["post"], name="book_return", url_path="return")
    def book_return(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "Book already returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrowing.book.inventory += 1
        borrowing.book.save()

        borrowing.actual_return_date = timezone.now()
        borrowing.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
