from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import OTP
from users.tasks import send_otp_email


@receiver(post_save, sender=OTP)
def send_otp(sender, instance, created, **kwargs):
    if created:
        send_otp_email.delay(instance.otp, instance.user.email)
