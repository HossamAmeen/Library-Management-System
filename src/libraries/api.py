from django.db.models import Count, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from libraries.filters import BookFilter, LibraryFilter
from libraries.helper import haversine
from libraries.models import Author, Book, BorrowHistory, Category, Library
from libraries.serializers import (AuthorSerializer, BookSerializer,
                                   BookTransactionSerializer,
                                   BorrowedBookSerializer, CategorySerializer,
                                   LibrarySerializer, ListBookSerializer,
                                   ListBorrowHistorySerializer)


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.order_by('-id')
    serializer_class = LibrarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LibraryFilter

    def get_queryset(self):
        # Get current location from request
        current_lat = self.request.query_params.get('lat')
        current_lon = self.request.query_params.get('lon')

        if not current_lat or not current_lon:
            return self.queryset

        nearby_libraries = []
        for library in Library.objects.all():
            distance = haversine(
                float(current_lat), float(current_lon),
                library.latitude, library.longitude)
            if distance <= 50:  # 50 km radius
                nearby_libraries.append(library.id)

        return Library.objects.filter(id__in=nearby_libraries)


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


class BorrowHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        data = BorrowHistory.objects.filter(user=request.user).select_related(
            'book', 'user').order_by('-id')

        data = paginator.paginate_queryset(data, request)

        return paginator.get_paginated_response(ListBorrowHistorySerializer(
            data, many=True).data)

    def post(self, request):
        if self.request.user.borrowhistory_set.filter(returned_at__isnull=True).count() > 3: # noqa
            return Response({'message': "you can't borrow more 3 book"},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = BookTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        borrowed_books = serializer.save(user=request.user)
        borrowed_books_serializer = BorrowedBookSerializer(
            borrowed_books, many=True)
        return Response({
            "message": "Transaction successful",
            "borrowed_books": borrowed_books_serializer.data
        }, status=status.HTTP_200_OK)
