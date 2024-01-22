from rest_framework import serializers
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils import timezone
from accounts.models import OTP
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password', 'password2']

    def validate(self, data):
        # Validate that the two passwords match
        if data['username'] == data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        # Remove the password2 field from the validated data
        password2 = validated_data.pop('password2', None)

        # Ensure that the passwords match again
        if validated_data['password'] != password2:
            raise serializers.ValidationError("Passwords do not match.")

        # Create a new user instance
        user = get_user_model().objects.create_user(**validated_data)

        # Generate 5-digit OTP
        otp_code = get_random_string(length=5, allowed_chars='0123456789')
        expiration_time = timezone.now() + timezone.timedelta(minutes=5)

        # Save OTP details
        OTP.objects.create(user=user, otp_code=otp_code, expiration_time=expiration_time)

        # Send OTP to user's email
        send_mail(
                'Your OTP for Registration',
                f'Hello {user.username}, Welcome to BlogAPI, Your OTP is: {otp_code}, It is valid for 5 Minutes Only!',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )

        return user

class OTPValidationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=5)
    email = serializers.EmailField()

    class Meta:
        model = OTP

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def __init__(self, instance=None, *args, **kwargs):
        self.otp_instance = instance
        super().__init__(*args, **kwargs)

    def is_expired(self):
        if self.otp_instance:
            return timezone.now() > (self.otp_instance.created_at + timezone.timedelta(minutes=5))
        return False

    def reset_expiration(self):
        if self.otp_instance:
            # Reset the created_at attribute to the current time
            self.otp_instance.created_at = timezone.now()
            self.otp_instance.save()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError({'CredentialsError': 'Invalid Credentials Entered!'})

        user = authenticate(email=email, password=password)

        if user:
            if not user.is_verified:
                raise serializers.ValidationError({'NotVerified': 'Account is not Verified, Verify it with OTP'})

            # Additional validation logic
            
            # Issue tokens
            refresh = RefreshToken.for_user(user)
            tokens = {'refresh': str(refresh), 'access': str(refresh.access_token)}

            return {'message': 'Login Successful!', 'tokens': tokens}
        else:
            raise serializers.ValidationError({'CredentialsError': 'Invalid Credentials Entered!'})