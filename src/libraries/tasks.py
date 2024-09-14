# library/tasks.py
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


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
