# library/tasks.py
import datetime

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from libraries.models import Borrow


@shared_task
def send_confirmation_email(user_email, book_title):
    subject = 'Book Borrow Confirmation'
    message = f'Thank you for borrowing {book_title}.'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )


@shared_task
def send_borrowed_books_email():
    twenty_seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=27)
    borrowed_books = Borrow.objects.filter(
        is_returnd=False, borrowed_at__gte=twenty_seven_days_ago)
    if borrowed_books.exists():
        subject = 'Daily Borrowed Books'
        message = 'Books borrowed today:\n\n'
        for book in borrowed_books:
            message += f'{book.user} borrowed {book.book_title} on {book.borrowed_date}\n'
        send_mail(
            subject,
            message,
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
@shared_task
def send_five_minute_updates():
    subject = 'Book Borrow Confirmation'
    message = 'Thank you for borrowing.'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        ["hosamameen948@gmail.com"],
        fail_silently=False,
    )
