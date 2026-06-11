"""
accounts/permissions.py — Custom permissions cho Markdown Social Hub.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Chỉ cho phép chủ sở hữu sửa/xóa nội dung của chính họ.
    Đọc (GET, HEAD, OPTIONS) thì ai cũng được.
    """

    message = "Bạn không có quyền chỉnh sửa tài nguyên này. Chỉ chủ sở hữu mới có thể thực hiện."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Kiểm tra field 'author' hoặc 'user' hoặc 'created_by'
        owner = (
            getattr(obj, "author", None)
            or getattr(obj, "user", None)
            or getattr(obj, "created_by", None)
        )
        return owner == request.user


class IsOwner(BasePermission):
    """Chỉ chủ sở hữu mới được truy cập (không cho đọc)."""

    message = "Bạn không có quyền truy cập tài nguyên này."

    def has_object_permission(self, request, view, obj):
        owner = (
            getattr(obj, "author", None)
            or getattr(obj, "user", None)
            or getattr(obj, "created_by", None)
        )
        return owner == request.user
