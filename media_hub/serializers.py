"""
media_hub/serializers.py — Serializers cho Media upload.
"""

from rest_framework import serializers
from .models import Media

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]


class MediaSerializer(serializers.ModelSerializer):
    """Serializer để upload và xem media."""

    uploaded_by_username = serializers.CharField(source="uploaded_by.username", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = [
            "id", "file", "file_url", "original_name",
            "file_size", "uploaded_by_username", "created_at",
        ]
        read_only_fields = ["id", "original_name", "file_size", "uploaded_by_username", "created_at", "file_url"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def validate_file(self, value):
        # Kiểm tra content type
        content_type = getattr(value, "content_type", "")
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                f"Chỉ chấp nhận các định dạng ảnh: {', '.join(ALLOWED_CONTENT_TYPES)}. "
                f"File của bạn có kiểu: {content_type}"
            )
        # Kiểm tra kích thước file
        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"File quá lớn ({value.size / (1024 * 1024):.2f} MB). "
                f"Giới hạn tối đa là {MAX_FILE_SIZE // (1024 * 1024)} MB."
            )
        return value

    def create(self, validated_data):
        file = validated_data["file"]
        validated_data["original_name"] = file.name
        validated_data["file_size"] = file.size
        return super().create(validated_data)
