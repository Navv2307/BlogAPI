from django.urls import path
from .views import RegistrationView, OTPValidationView, ResendOTPView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('validate-otp/', OTPValidationView.as_view(), name='validate-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
]