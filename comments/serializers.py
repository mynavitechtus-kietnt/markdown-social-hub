"""
comments/serializers.py — Serializers cho Comment.
"""

from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer cho bình luận."""

    author_username = serializers.CharField(source="author.username", read_only=True)
    post_title = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id", "post", "post_title", "author_username",
            "content", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author_username", "post_title", "created_at", "updated_at"]

    def validate_content(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Nội dung bình luận phải có ít nhất 2 ký tự.")
        if len(value) > 2000:
            raise serializers.ValidationError("Nội dung bình luận không được vượt quá 2000 ký tự.")
        return value.strip()

    def validate(self, data):
        """Chỉ được bình luận bài viết đang ở trạng thái Publish."""
        from posts.models import Post
        post = data.get("post")
        if post and post.status != Post.Status.PUBLISH:
            raise serializers.ValidationError(
                {"post": "Chỉ có thể bình luận trên bài viết đã được Công khai."}
            )
        return data
