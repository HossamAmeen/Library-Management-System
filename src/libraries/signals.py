from django.db.models.signals import post_save
from django.dispatch import receiver

from libraries.models import BorrowHistory

from .tasks import send_confirmation_email


@receiver(post_save, sender=BorrowHistory)
def send_borrow_confirmation(sender, instance, created, **kwargs):
    if created:
        send_confirmation_email.delay(instance.user.email, instance.book.title)
