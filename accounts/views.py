"""
accounts/views.py — Views xác thực và quản lý hồ sơ người dùng.
"""

import logging
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from typing import cast

from .models import UserProfile
from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)

logger = logging.getLogger("accounts")


class CustomTokenObtainPairView(TokenObtainPairView):
    """Đăng nhập — trả về JWT token với custom payload."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            data = cast(dict, request.data)
            username = data.get("username", "")
            logger.info(f"User login: {username}")
        return response


class RegisterView(generics.CreateAPIView):
    """Đăng ký tài khoản mới — không yêu cầu xác thực."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"New user registered: {user.username} (ID={user.pk})")
        return Response(
            {
                "message": "Đăng ký thành công! Vui lòng đăng nhập để lấy token.",
                "user": {"id": user.pk, "username": user.username, "email": user.email},
            },
            status=status.HTTP_201_CREATED,
        )


class MyProfileView(generics.RetrieveUpdateAPIView):
    """Xem và cập nhật hồ sơ cá nhân của user đang đăng nhập."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"User {request.user.username} updated their profile.")
        return Response(serializer.data)
