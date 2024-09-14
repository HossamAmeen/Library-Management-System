from rest_framework.routers import DefaultRouter

from libraries.api import (AuthorViewSet, BookViewSet, BorrowViewSet,
                           CategoryViewSet, LibraryViewSet)

router = DefaultRouter()
router.register(r'libraries', LibraryViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'borrows', BorrowViewSet)

urlpatterns = router.urls
