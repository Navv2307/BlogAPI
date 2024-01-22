from django.urls import path
from .views import RegistrationView, OTPValidationView, ResendOTPView, LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('validate-otp/', OTPValidationView.as_view(), name='validate-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='custom_login'),
    path('accesstoken/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accesstoken/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]