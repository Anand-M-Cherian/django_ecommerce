from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from .serializers import SignUpSerializer, UserSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from utils.helpers import get_current_host

# Create your views here.

@api_view(['POST'])
def register(request):
    data = request.data.copy()  # Make a mutable copy
    data['username'] = data['email']  # Set username as email
    signUpSerializer = SignUpSerializer(data=data)

    if signUpSerializer.is_valid():
        if not User.objects.filter(username=data['email']).exists():
            signUpSerializer.save()
            return Response({"message": "User has been registered."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(signUpSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    userSerializer = UserSerializer(user)
    return Response(userSerializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data.copy()  # Make a mutable copy

    userSerializer = UserSerializer(user, data=data, partial=True)
    if userSerializer.is_valid():
        userSerializer.save()
        return Response(userSerializer.data, status=status.HTTP_200_OK)
    else:
        return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def forgot_password(request):
    data = request.data
    email = data.get('email')
    user = get_object_or_404(User, email=email)

    # Generate a random token and set an expiry time
    token = get_random_string(length=40)
    expire_time = datetime.now() + timedelta(minutes=30)

    user.profile.reset_password_token = token
    user.profile.reset_password_token_expiry = expire_time
    user.profile.save()

    # Here you would typically send an email to the user with the reset link
    domain = get_current_host(request)
    reset_link = f"{domain}/api/reset-password/{token}/"
    body = f"Click the link to reset your password: {reset_link}"
    send_mail(
        'Password Reset Request',
        body,
        'trustmeifyoucan@server.com',
        [email],
    )

    return Response({"message": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(User, profile__reset_password_token=token)

    # Check if the token has expired
    if user.profile.reset_password_token_expiry.replace(tzinfo=None) < datetime.now():
        return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate the new password
    if data['password'] != data['confirm_password']:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update the user's password
    user.set_password(data['password'])
    user.save()

    # Clear the reset token and expiry
    user.profile.reset_password_token = ''
    user.profile.reset_password_token_expiry = None
    user.profile.save()

    return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)