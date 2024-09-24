import random

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import OTP, Reader

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        # User don't have confirm_password
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        self.tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
        return self.tokens


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        self.user = User.objects.filter(email=data['email']).first()
        if not self.user:
            raise ValidationError({"message": "this email not found"})

        return super().validate(data)

    def create(self, validated_data):
        otp = str(random.randint(100000, 999999))
        otp_instance = OTP.objects.create(user=self.user, otp=otp)
        return otp_instance

    def to_representation(self, instance):
        return {'message': 'If your email is registered, you will '
                           'receive an OTP shortly'}


class PasswordResetConfirmSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "Passwords must match."})

        self.user = User.objects.filter(email=data['email']).first()
        if not self.user:
            raise ValidationError({"message": "this email not found"})
        return data

    def create(self, validated_data):
        otp_instance = OTP.objects.filter(
            user=self.user, otp=validated_data['otp']).first()
        if otp_instance and otp_instance.is_valid():
            self.user.set_password(validated_data['password'])
            self.user.save()
            otp_instance.delete()
            return otp_instance
        raise ValidationError({'message': 'Invalid or expired OTP'})

    def to_representation(self, instance):
        return {'message': 'Password reset successful'}


class ReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = ['username', 'email']
