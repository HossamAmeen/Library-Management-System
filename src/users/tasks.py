from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_otp_email(otp, user_email):
    send_mail(
        "Reset Password",
        f'Your OTP: {otp}',
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )
