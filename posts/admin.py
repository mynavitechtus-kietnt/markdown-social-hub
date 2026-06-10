from django.contrib import admin
from .models import Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 30


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "created_at", "updated_at"]
    list_filter = ["status", "created_at", "author"]
    search_fields = ["title", "content", "author__username"]
    readonly_fields = ["id", "created_at", "updated_at"]
    filter_horizontal = ["tags"]
    list_per_page = 20
    ordering = ["-created_at"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("tags")
        )
