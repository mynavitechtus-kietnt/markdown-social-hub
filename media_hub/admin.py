from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ["original_name", "uploaded_by", "file_size", "created_at"]
    list_filter = ["created_at", "uploaded_by"]
    search_fields = ["original_name", "uploaded_by__username"]
    readonly_fields = ["id", "original_name", "file_size", "created_at"]
    list_per_page = 20
