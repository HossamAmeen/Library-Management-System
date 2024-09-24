import django_filters
from django.db.models import Count, Prefetch, Q

from libraries.models import Author, Book, Library


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


class AuthorFilter(django_filters.FilterSet):

    class Meta:
        model = Author
        fields = []

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        author_filters = Q()
        book_filters = Q()
        book_category = self.request.query_params.get('book_category', None)
        library = self.request.query_params.get('library', None)

        if book_category:
            author_filters &= Q(book__category__name__icontains=book_category)
            book_filters &= Q(category__name__icontains=book_category)

        if library:
            author_filters &= Q(book__library__name__icontains=library)
            book_filters &= Q(library__name__icontains=library)

        book_query = Book.objects.filter(book_filters).select_related('category') # noqa

        queryset = queryset.prefetch_related(
            Prefetch('book_set', queryset=book_query))
        queryset = queryset.filter(author_filters).annotate(
            book_count=Count('book', filter=author_filters)
        )

        return queryset
