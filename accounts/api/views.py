from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, OTPValidationSerializer, ResendOTPSerializer
from accounts.models import OTP
from accounts.models import CustomUser
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registration successful. OTP sent to your email.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPValidationView(APIView):
    def post(self, request):
        serializer = OTPValidationSerializer(data=request.data)

        if serializer.is_valid():
            otp_code = serializer.validated_data.get('otp_code')
            user_email = serializer.validated_data.get('email')

            # Check if the OTP exists and is associated with the correct user
            try:
                otp_instance = OTP.objects.get(otp_code=otp_code, user__email=user_email)
            except OTP.DoesNotExist:
                return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            # Checking for OTP Expiration
            if otp_instance.is_expired():
                return Response({'message': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)

            user_instance = CustomUser.objects.get(email=user_email)
            user_instance.is_verified = True
            user_instance.save()

            return Response({'message': 'OTP is valid.'}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(instance=None, data=request.data)

        if serializer.is_valid():
            user_email = serializer.validated_data.get('email')

            try:
                user_instance = CustomUser.objects.get(email=user_email)
            except CustomUser.DoesNotExist:
                return Response({'message': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a new 5-digit OTP
            new_otp_code = get_random_string(length=5, allowed_chars='0123456789')
            
            # Update or create OTP details
            otp_instance, created = OTP.objects.update_or_create(
                user=user_instance,
                defaults={'otp_code': new_otp_code, 'expiration_time': timezone.now() + timezone.timedelta(minutes=5)}
            )

            # Update created_at field
            otp_instance.created_at = timezone.now()
            otp_instance.save()

            # Send the new OTP to the user's email
            send_mail(
                'Your New OTP',
                f'Your new OTP is: {new_otp_code}',
                'from@example.com',
                [user_email],
                fail_silently=False,
            )

            return Response({'message': 'New OTP has been sent.'}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)