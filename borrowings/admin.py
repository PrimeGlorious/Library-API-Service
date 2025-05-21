from django.contrib import admin
from .models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "user",
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "is_paid",
    )
    list_filter = (
        "is_paid",
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
    )
    search_fields = ("book__title", "user__email")
    ordering = ("-borrow_date",)
