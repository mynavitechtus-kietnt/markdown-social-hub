"""
comments/models.py — Model Bình luận bài viết.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Comment(models.Model):
    """Bình luận của người dùng cho một bài viết."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Bài viết",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Tác giả bình luận",
    )
    content = models.TextField(verbose_name="Nội dung bình luận")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        verbose_name = "Bình luận"
        verbose_name_plural = "Bình luận"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on '{self.post.title[:30]}'"
