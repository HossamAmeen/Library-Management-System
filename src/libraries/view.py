from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from libraries.filters import AuthorFilter, BookFilter, LibraryFilter
from libraries.helper import haversine
from libraries.models import Author, Book, BorrowHistory, Category, Library
from libraries.serializers import (AuthorSerializer, BookSerializer,
                                   BookTransactionSerializer,
                                   CategorySerializer,
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilter


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


class BorrowHistoryAPI(generics.ListCreateAPIView):
    queryset = BorrowHistory.objects.select_related(
        'book', 'user').order_by('-id')
    permission_classes = [IsAuthenticated]
    serializer_class = ListBorrowHistorySerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListBorrowHistorySerializer
        else:
            return BookTransactionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
