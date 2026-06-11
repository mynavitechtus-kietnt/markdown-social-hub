from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCommentAuthorOrReadOnly(BasePermission):
    """Chỉ tác giả comment mới được sửa/xóa."""

    message = "Bạn không có quyền chỉnh sửa bình luận này. Chỉ tác giả mới có thể thực hiện."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
