"""
media_hub/views.py — Views cho Media upload và quản lý.
"""

import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Media
from .serializers import MediaSerializer
from accounts.permissions import IsOwnerOrReadOnly

logger = logging.getLogger("media_hub")


class MediaViewSet(viewsets.ModelViewSet):
    """
    Upload và quản lý media (hình ảnh).
    - list: xem media của chính mình
    - create: upload ảnh mới
    - retrieve: xem chi tiết
    - destroy: xóa (chỉ chủ sở hữu)
    - update/partial_update: không hỗ trợ
    """

    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        """Chỉ trả về media của user đang đăng nhập."""
        return (
            Media.objects.select_related("uploaded_by")
            .filter(uploaded_by=self.request.user)
            .order_by("-created_at")
        )

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save(uploaded_by=self.request.user)
        logger.info(
            f"Media uploaded by {self.request.user.username}: "
            f"{instance.original_name} ({instance.file_size} bytes)"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Xóa file vật lý khỏi storage
        if instance.file:
            instance.file.delete(save=False)
        logger.warning(
            f"Media deleted by {request.user.username}: {instance.original_name} (ID={instance.pk})"
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
