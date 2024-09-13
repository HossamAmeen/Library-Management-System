import django_filters

from libraries.models import Author, Library, Book


class LibraryFilter(django_filters.FilterSet):
    book_category = django_filters.CharFilter(
        field_name='book__category__name', lookup_expr='icontains')
    author = django_filters.CharFilter(
        field_name='book__author__name', lookup_expr='icontains')

    class Meta:
        model = Library
        fields = ['book_category', 'author']


class BookFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name='category__name', lookup_expr='icontains')
    library = django_filters.CharFilter(
        field_name='library__name', lookup_expr='icontains')
    author = django_filters.CharFilter(
        field_name='author__name', lookup_expr='icontains')

    class Meta:
        model = Book
        fields = ['category', 'library', 'author']
