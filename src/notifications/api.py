from rest_framework.viewsets import ModelViewSet

from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated


class NotificationViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Notification.objects.order_by('-id')
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
