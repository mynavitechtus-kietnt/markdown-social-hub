from rest_framework import serializers
from .models import Post, Tag


# ==================== Tag ====================
class TagSerializer(serializers.ModelSerializer):

    post_count = serializers.SerializerMethodField()

    def get_post_count(self, obj):
        return obj.posts.filter(status=Post.Status.PUBLISH).count()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Tên nhãn phải có ít nhất 2 ký tự.")
        return value

    def validate_slug(self, value):
        import re

        if not re.match(r"^[a-z0-9-]+$", value):
            raise serializers.ValidationError(
                "Slug chỉ được chứa chữ thường, số và dấu gạch ngang."
            )
        return value

    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "post_count"]


# ==================== Post ====================
class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "status",
            "author_username",
            "tags",
            "comment_count",
            "created_at",
            "updated_at",
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source="tags",
        write_only=True,
        required=False,
    )
    comment_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Tiêu đề phải có ít nhất 5 ký tự.")
        return value.strip()

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Nội dung phải có ít nhất 10 ký tự.")
        return value

    def validate_status(self, value):
        if value not in [Post.Status.DRAFT, Post.Status.PUBLISH]:
            raise serializers.ValidationError(
                f"Trạng thái không hợp lệ. Chỉ chấp nhận: {[s.value for s in Post.Status]}"
            )
        return value

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "status",
            "author_username",
            "tags",
            "tag_ids",
            "comment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author_username", "created_at", "updated_at"]

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        post = Post.objects.create(**validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
