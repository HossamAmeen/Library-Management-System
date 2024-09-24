from django.urls import path
from rest_framework.routers import DefaultRouter

from libraries.view import (AuthorViewSet, BookViewSet, BorrowHistoryAPI,
                            CategoryViewSet, LibraryViewSet)

router = DefaultRouter()
router.register(r'libraries', LibraryViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('borrow-histories/', BorrowHistoryAPI.as_view()),
]
