import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Post, Tag
from .serializers import PostListSerializer, PostDetailSerializer, TagSerializer
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger("posts")


class TagViewSet(viewsets.ModelViewSet):
    """
    CRUD Tags.
    - list, retrieve: AllowAny
    - create, update, destroy: IsAuthenticated
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]


class PostViewSet(viewsets.ModelViewSet):
    """
    CRUD Post.
    - list, retrieve (publish only): AllowAny
    - create: IsAuthenticated
    - update, partial_update, destroy: IsAuthenticated + IsOwnerOrReadOnly
    - my_posts: xem bài viết của chính mình (cả draft lẫn publish)
    """

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    def get_queryset(self):
        """
        - Anonymous & list: chỉ trả về bài PUBLISH.
        - Authenticated user xem my_posts: trả về bài của chính họ (cả draft).
        - Authenticated user xem detail: trả về nếu là PUBLISH hoặc là tác giả.
        """
        user = self.request.user

        # Custom action my_posts: chỉ bài của user đang đăng nhập
        if self.action == "my_posts":
            if user.is_authenticated:
                return (
                    Post.objects.select_related("author")
                    .prefetch_related("tags", "comments")
                    .filter(author=user)
                )
            return Post.objects.none()

        # Detail: tác giả xem được cả draft của mình
        if self.action == "retrieve" and user.is_authenticated:
            return Post.objects.select_related("author").prefetch_related(
                "tags", "comments"
            ).filter(status=Post.Status.PUBLISH) | Post.objects.select_related(
                "author"
            ).prefetch_related(
                "tags", "comments"
            ).filter(
                author=user
            )

        # Mặc định: chỉ PUBLISH
        queryset = (
            Post.objects.select_related("author")
            .prefetch_related("tags", "comments")
            .filter(status=Post.Status.PUBLISH)
        )

        # --- Filters ---
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)

        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        author = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(author__username=author)

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        logger.info(
            f"Post created by {self.request.user.username}: {serializer.instance.title}"
        )

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        logger.warning(
            f"Post deleted by {request.user.username}: '{post.title}' (ID={post.pk})"
        )
        return super().destroy(request, *args, **kwargs)

    # ---- Custom Actions ----

    @action(
        detail=False,
        methods=["get"],
        url_path="my-posts",
        permission_classes=[IsAuthenticated],
    )
    def my_posts(self, request):
        """GET /api/posts/my-posts/ — Xem tất cả bài viết của tôi (cả draft lẫn publish)."""
        queryset = self.get_queryset()

        status_filter = request.query_params.get("status")
        if status_filter in [Post.Status.DRAFT, Post.Status.PUBLISH]:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="publish",
        permission_classes=[IsAuthenticated, IsOwnerOrReadOnly],
    )
    def publish(self, request, pk=None):
        """POST /api/posts/{id}/publish/ — Đổi trạng thái sang Publish."""
        post = self.get_object()
        if post.status == Post.Status.PUBLISH:
            return Response({"message": "Bài viết đã ở trạng thái Công khai."})
        post.status = Post.Status.PUBLISH
        post.save(update_fields=["status", "updated_at"])
        logger.info(f"Post published by {request.user.username}: '{post.title}'")
        return Response({"message": "Đã đăng công khai bài viết.", "id": str(post.pk)})

    @action(
        detail=True,
        methods=["post"],
        url_path="draft",
        permission_classes=[IsAuthenticated, IsOwnerOrReadOnly],
    )
    def draft(self, request, pk=None):
        """POST /api/posts/{id}/draft/ — Đổi trạng thái sang Draft."""
        post = self.get_object()
        if post.status == Post.Status.DRAFT:
            return Response({"message": "Bài viết đang ở trạng thái Nháp."})
        post.status = Post.Status.DRAFT
        post.save(update_fields=["status", "updated_at"])
        logger.info(f"Post set to draft by {request.user.username}: '{post.title}'")
        return Response(
            {"message": "Đã chuyển bài viết về trạng thái Nháp.", "id": str(post.pk)}
        )
