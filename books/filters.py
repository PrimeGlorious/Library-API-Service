import django_filters
from books.models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title", lookup_expr="icontains"
    )
    author = django_filters.CharFilter(
        field_name="author", lookup_expr="icontains"
    )
    cover = django_filters.ChoiceFilter(
        field_name="cover", choices=Book.CoverChoices.choices
    )

    daily_fee_min = django_filters.NumberFilter(
        field_name="daily_fee", lookup_expr="gte"
    )
    daily_fee_max = django_filters.NumberFilter(
        field_name="daily_fee", lookup_expr="lte"
    )

    inventory_min = django_filters.NumberFilter(
        field_name="inventory", lookup_expr="gte"
    )
    inventory_max = django_filters.NumberFilter(
        field_name="inventory", lookup_expr="lte"
    )

    class Meta:
        model = Book
        fields = ["title", "author", "cover"]
