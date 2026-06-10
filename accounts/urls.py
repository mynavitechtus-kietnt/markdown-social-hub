"""
accounts/urls.py — URL routing cho xác thực.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import CustomTokenObtainPairView, RegisterView, MyProfileView

urlpatterns = [
    # Đăng ký tài khoản
    path("register/", RegisterView.as_view(), name="auth-register"),
    # Đăng nhập — lấy JWT token
    path("login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    # Refresh token
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    # Verify token
    path("token/verify/", TokenVerifyView.as_view(), name="auth-token-verify"),
    # Hồ sơ cá nhân
    path("profile/", MyProfileView.as_view(), name="auth-profile"),
]
