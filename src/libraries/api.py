from django.db.models import Count, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from libraries.filters import BookFilter, LibraryFilter
from libraries.models import Author, Book, Borrow, Category, Library
from libraries.serializers import (AuthorSerializer, BookSerializer,
                                   BorrowModificationSerializer,
                                   BorrowSerializer, CategorySerializer,
                                   LibrarySerializer, ListBookSerializer,
                                   ListBorrowSerializer)


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


class BorrowViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Borrow.objects.select_related('book', 'user')

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListBorrowSerializer
        if self.request.method == "PATCH":
            return BorrowModificationSerializer
        return BorrowSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        if self.request.user.borrow_set.filter(is_returnd=False).count() > 3:
            return Response({'message': "you can't borrow more 3 book"},
                            status=status.HTTP_400_BAD_REQUEST)
        request_data = request.data
        for request_item in request_data:
            request_item['user'] = request.user.id

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
