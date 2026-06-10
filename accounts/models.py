import uuid
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Người dùng",
    )
    bio = models.TextField(blank=True, verbose_name="Giới thiệu bản thân")
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Ảnh đại diện",
    )
    # JSONB: lưu cấu hình cá nhân (màu nền, font size, theme...)
    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Cấu hình cá nhân",
        help_text='Ví dụ: {"bg_color": "#ffffff", "font_size": 14, "theme": "light"}',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"

    def __str__(self):
        return f"Profile of {self.user.username}"
