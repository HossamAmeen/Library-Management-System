from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from users.view import (PasswordResetConfirmView, PasswordResetRequestView,
                        RegisterView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('password-reset/', PasswordResetRequestView.as_view(),
         name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
]
