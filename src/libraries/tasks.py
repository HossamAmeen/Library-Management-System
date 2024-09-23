# library/tasks.py
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from users.models import Reader


@shared_task
def send_confirmation_email(user_email, book_title):
    subject = 'Book BorrowHistory Confirmation'
    message = f'Thank you for borrowing {book_title}.'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )


@shared_task
def send_due_book_reminders():
    now = datetime.now()
    three_days_from_now = now + timedelta(days=3)
    readers = Reader.objects.filter(
        borrowhistory__should_returned_at__date__lte=three_days_from_now.date(), # noqa
        borrowhistory__should_returned_at__date__gte=now.date(),
        borrowhistory__returned_at__isnull=True).distinct()

    for reader in readers:
        books_history = reader.borrowhistory_set.filter(
            should_returned_at__date__lte=three_days_from_now.date(),
            should_returned_at__date__gte=now.date(),
            returned_at__isnull=True
        ).order_by('id')
    books_history = [f"{book_history.book.title} by {book_history.should_returned_at} \n" for book_history in books_history] # noqa
    send_mail(
        'Book Return Reminder',
        f'Dear {reader.username},\n\n'
        f'This is a reminder to return the book(s) {"".join(books_history)}'
        'Thank you!',
        settings.EMAIL_HOST_USER,
        [reader.email],
        fail_silently=False,
    )
