"""
media_hub/models.py — Model lưu trữ media (hình ảnh) do người dùng tải lên.
"""

import uuid
import os
from django.db import models
from django.contrib.auth.models import User


def media_upload_path(instance, filename):
    """Tổ chức thư mục upload theo user ID."""
    ext = filename.rsplit(".", 1)[-1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads", str(instance.uploaded_by.id), new_filename)


class Media(models.Model):
    """File media (hình ảnh) được tải lên bởi user."""

    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ImageField(
        upload_to=media_upload_path,
        verbose_name="File ảnh",
    )
    original_name = models.CharField(max_length=255, verbose_name="Tên file gốc")
    file_size = models.PositiveIntegerField(default=0, verbose_name="Kích thước file (bytes)")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="media_files",
        verbose_name="Người tải lên",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Media"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.original_name} (by {self.uploaded_by.username})"
