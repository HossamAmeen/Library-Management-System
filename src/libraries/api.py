from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from django.db.models import Prefetch
from libraries.filters import LibraryFilter, BookFilter
from libraries.models import Author, Book, Category, Library
from libraries.serializers import (AuthorSerializer, BookSerializer,
                                   CategorySerializer, LibrarySerializer, ListBookSerializer)


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.order_by('-id')
    serializer_class = LibrarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LibraryFilter


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.order_by('-id')
    serializer_class = AuthorSerializer

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


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('-id')
    serializer_class = CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category', 'author')\
        .order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListBookSerializer
        else:
            return BookSerializer
