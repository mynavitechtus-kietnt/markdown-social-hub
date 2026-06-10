from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile

# ==================== JWT Custom ====================


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Thêm thông tin user vào JWT payload."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        return token


# ==================== Register ====================


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer đăng ký tài khoản mới."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được sử dụng.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Mật khẩu xác nhận không khớp."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        # Tự động tạo UserProfile
        UserProfile.objects.create(user=user)
        return user


# ==================== UserProfile ====================


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer đọc/cập nhật hồ sơ cá nhân."""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "bio",
            "avatar",
            "preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "username", "email", "created_at", "updated_at"]

    def validate_preferences(self, value):
        """Đảm bảo preferences là dict hợp lệ."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Preferences phải là một JSON object.")
        allowed_keys = {"bg_color", "font_size", "theme", "language"}
        unknown_keys = set(value.keys()) - allowed_keys
        if unknown_keys:
            raise serializers.ValidationError(
                f"Các key không hợp lệ: {unknown_keys}. Chỉ chấp nhận: {allowed_keys}"
            )
        if "font_size" in value:
            font_size = value["font_size"]
            if not isinstance(font_size, int) or not (10 <= font_size <= 32):
                raise serializers.ValidationError(
                    "font_size phải là số nguyên từ 10 đến 32."
                )
        if "theme" in value and value["theme"] not in ("light", "dark"):
            raise serializers.ValidationError(
                "theme chỉ chấp nhận 'light' hoặc 'dark'."
            )
        return value
