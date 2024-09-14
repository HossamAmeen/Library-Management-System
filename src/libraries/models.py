from django.db import models

from users.models import Reader


class Library(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)


class Author(models.Model):
    name = models.CharField(max_length=255)


class Category(models.Model):
    name = models.CharField(max_length=255)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    quantiy = models.IntegerField(default=0)
    available = models.BooleanField(default=True)


class Borrow(models.Model):
    user = models.ForeignKey(Reader, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    is_returnd = models.BooleanField(default=False)
