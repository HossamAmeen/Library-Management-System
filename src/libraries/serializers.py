from rest_framework import serializers

from libraries.models import Author, Book, Category, Library


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookWithCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Book
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    books = BookWithCategorySerializer(source="book_set", read_only=True,
                                       many=True)
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = '__all__'


class SingleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class ListBookSerializer(serializers.ModelSerializer):
    author = SingleAuthorSerializer()
    category = CategorySerializer()

    class Meta:
        model = Book
        fields = '__all__'
