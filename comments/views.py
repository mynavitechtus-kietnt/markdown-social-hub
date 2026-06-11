"""
comments/views.py — Views cho Comment.
"""

import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsCommentAuthorOrReadOnly

logger = logging.getLogger("comments")


class CommentViewSet(viewsets.ModelViewSet):
    """
    CRUD cho Comment.
    - list, retrieve: AllowAny
    - create: IsAuthenticated
    - update, partial_update, destroy: IsAuthenticated + IsCommentAuthorOrReadOnly
    """

    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action == "create":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsCommentAuthorOrReadOnly()]

    def get_queryset(self):
        queryset = (
            Comment.objects.select_related("author", "post")
            .all()
        )

        # Filter theo post
        post_id = self.request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(post__id=post_id)

        # Filter theo author
        author = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(author__username=author)

        return queryset

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        logger.info(
            f"Comment created by {self.request.user.username} "
            f"on post '{comment.post.title[:30]}'"
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        logger.warning(
            f"Comment deleted by {request.user.username} (ID={comment.pk})"
        )
        return super().destroy(request, *args, **kwargs)
