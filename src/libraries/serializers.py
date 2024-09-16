from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from rest_framework import serializers

from libraries.models import Author, Book, BorrowHistory, Category, Library
from users.serializers import ReadSerializer


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


class SingleBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'


class ListBorrowHistorySerializer(serializers.ModelSerializer):
    book = SingleBookSerializer()
    user = ReadSerializer()
    penalty = serializers.SerializerMethodField()

    class Meta:
        model = BorrowHistory
        fields = "__all__"

    def get_penalty(self, obj):
        if obj.returned_at:
            days_difference = (obj.should_returned_at - obj.borrowed_at).days
            penalty = max(0, days_difference - 30)
            return penalty
        return 0


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    should_returned_at = serializers.DateTimeField(required=False)


class BookTransactionSerializer(serializers.Serializer):
    borrow_books = BorrowBookSerializer(many=True, required=False)
    return_books = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    def save(self, user):
        borrowed_books = []
        if 'borrow_books' in self.validated_data:
            for item in self.validated_data['borrow_books']:
                book = Book.objects.filter(id=item['book_id']).first()
                if not book:
                    raise serializers.ValidationError(
                        f"Book with id {item['book_id']} does not exist.")
                if not book.available:
                    raise serializers.ValidationError({
                       "message": f"The book '{book.title}' is not available."}
                    )

                borrow_book_data = {
                    "user": user, "book": book
                }
                should_returned_at = item.get('should_returned_at')
                if should_returned_at:
                    if should_returned_at < timezone.now():
                        raise serializers.ValidationError(
                            "The should_returned_at date cannot be in the past.")
                    if should_returned_at.date() > (timezone.now() + timedelta(days=30)).date(): # noqa
                        raise serializers.ValidationError(
                            "The should_returned_at date cannot be greater "
                            "than 30 days from today.")

                    borrow_book_data['should_returned_at'] = \
                        item['should_returned_at']
                else:
                    borrow_book_data['should_returned_at'] = \
                        (datetime.now() + timedelta(days=30))
                borrow_history = BorrowHistory.objects.create(
                    **borrow_book_data)
                book.available = False
                book.save()
                borrowed_books.append(borrow_history)

        if 'return_books' in self.validated_data:
            book_ids = self.validated_data['return_books']
            histories = BorrowHistory.objects.filter(
                book_id__in=book_ids, user=user, returned_at__isnull=True)
            for history in histories:
                history.returned_at = datetime.now()
                history.save()
                book = history.book
                book.available = True
                book.save()
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "notifications",
                    {
                        "type": "book_available",
                        "title": book.title
                    }
                )

        return borrowed_books


class BorrowedBookSerializer(serializers.ModelSerializer):
    should_returned_at = serializers.DateTimeField()

    class Meta:
        model = BorrowHistory
        fields = ['book', 'borrowed_at', 'should_returned_at']
