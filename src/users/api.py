import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import OTP
from users.serializers import (LoginSerializer, PasswordResetConfirmSerializer,
                               PasswordResetRequestSerializer,
                               RegisterSerializer)

User = get_user_model()


class RegisterView(views.APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'access': access_token,
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'access': access_token,
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class PasswordResetRequestView(views.APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            otp = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp=otp)
            email_body = f'you OTP: {otp}'
            send_mail("Reset Password", email_body, settings.EMAIL_HOST_USER,
                      [email])
            return Response({'message': 'If your email is registered, you will'
                                        ' receive an OTP shortly'},
                            status=status.HTTP_200_OK)


class PasswordResetConfirmView(views.APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        password = serializer.validated_data['password']
        user = User.objects.filter(email=email).first()
        if user:
            otp_instance = OTP.objects.filter(user=user, otp=otp).first()
            if otp_instance and otp_instance.is_valid():
                user.set_password(password)
                user.save()
                otp_instance.delete()
                return Response({'message': 'Password reset successful'},
                                status=status.HTTP_200_OK)
            return Response({'message': 'Invalid or expired OTP'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
