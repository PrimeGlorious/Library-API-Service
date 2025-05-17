import django_filters
from .models import Book


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

    class Meta:
        model = Book
        fields = ["title", "author", "cover"]
