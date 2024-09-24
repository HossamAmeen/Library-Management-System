from django.contrib.auth import get_user_model
from rest_framework import generics

from users.serializers import (PasswordResetConfirmSerializer,
                               PasswordResetRequestSerializer,
                               RegisterSerializer)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer


class PasswordResetConfirmView(generics.CreateAPIView):
    serializer_class = PasswordResetConfirmSerializer
