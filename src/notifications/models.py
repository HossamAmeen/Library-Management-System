from django.db import models

from users.models import Reader


class Notification(models.Model):
    user = models.ForeignKey(Reader, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
