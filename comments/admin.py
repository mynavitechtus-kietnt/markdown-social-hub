from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "content_preview", "created_at"]
    list_filter = ["created_at", "author"]
    search_fields = ["content", "author__username", "post__title"]
    readonly_fields = ["id", "created_at", "updated_at"]
    list_per_page = 20

    def content_preview(self, obj):
        return obj.content[:60] + "..." if len(obj.content) > 60 else obj.content

    content_preview.short_description = "Nội dung"
