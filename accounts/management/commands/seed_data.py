"""
accounts/management/commands/seed_data.py
Bơm dữ liệu mẫu vào database để test API.

Chạy: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from posts.models import Post, Tag
from comments.models import Comment


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu cho Markdown Social Hub"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("🌱 Bắt đầu tạo dữ liệu mẫu..."))

        # ========== USERS ==========
        users_data = [
            {"username": "admin_user", "email": "admin@example.com", "password": "Admin@123456", "is_staff": True, "is_superuser": True},
            {"username": "alice", "email": "alice@example.com", "password": "Alice@123456"},
            {"username": "bob", "email": "bob@example.com", "password": "Bob@123456"},
            {"username": "charlie", "email": "charlie@example.com", "password": "Charlie@123456"},
        ]

        users = {}
        for u in users_data:
            is_staff = u.pop("is_staff", False)
            is_superuser = u.pop("is_superuser", False)
            user, created = User.objects.get_or_create(
                username=u["username"],
                defaults={"email": u["email"], "is_staff": is_staff, "is_superuser": is_superuser},
            )
            if created:
                user.set_password(u["password"])
                user.save()
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "bio": f"Tôi là {user.username}, thành viên của Markdown Social Hub.",
                        "preferences": {"theme": "light", "font_size": 14},
                    },
                )
                self.stdout.write(f"  ✅ User tạo: {user.username}")
            else:
                self.stdout.write(f"  ⏭ User đã tồn tại: {user.username}")
            users[u["username"]] = user

        # ========== TAGS ==========
        tags_data = [
            {"name": "python", "slug": "python"},
            {"name": "django", "slug": "django"},
            {"name": "rest-api", "slug": "rest-api"},
            {"name": "docker", "slug": "docker"},
            {"name": "postgresql", "slug": "postgresql"},
            {"name": "tutorial", "slug": "tutorial"},
            {"name": "tips", "slug": "tips"},
        ]
        tags = {}
        for t in tags_data:
            tag, _ = Tag.objects.get_or_create(slug=t["slug"], defaults={"name": t["name"]})
            tags[t["slug"]] = tag
        self.stdout.write(f"  ✅ Tags tạo/đã có: {len(tags)}")

        # ========== POSTS ==========
        posts_data = [
            {
                "title": "Hướng dẫn Django REST Framework từ A đến Z",
                "content": """# Django REST Framework Tutorial

## Giới thiệu

Django REST Framework (DRF) là công cụ mạnh mẽ để xây dựng Web API.

## Cài đặt

```bash
pip install djangorestframework
```

## Cấu hình

Thêm `rest_framework` vào `INSTALLED_APPS`.

## Kết luận

DRF giúp bạn xây dựng API nhanh và chuẩn RESTful!
""",
                "author": "alice",
                "status": "publish",
                "tags": ["python", "django", "rest-api", "tutorial"],
            },
            {
                "title": "Docker Compose cho Django và PostgreSQL",
                "content": """# Docker Compose Setup

## Cấu trúc

```yaml
services:
  db:
    image: postgres:15-alpine
  web:
    build: .
    depends_on:
      - db
```

## Chạy

```bash
docker-compose up --build
```

## Volumes

Đừng quên cấu hình volumes để data không mất khi restart!
""",
                "author": "bob",
                "status": "publish",
                "tags": ["docker", "postgresql", "tutorial"],
            },
            {
                "title": "10 Mẹo Tối Ưu Query trong Django ORM",
                "content": """# Django ORM Optimization Tips

## 1. select_related

Dùng cho ForeignKey:

```python
Product.objects.select_related('category').all()
```

## 2. prefetch_related

Dùng cho ManyToMany:

```python
Post.objects.prefetch_related('tags').all()
```

## 3. Tránh N+1 Query

Luôn kiểm tra số lượng query bằng Django Debug Toolbar!
""",
                "author": "alice",
                "status": "publish",
                "tags": ["python", "django", "tips"],
            },
            {
                "title": "JWT Authentication với SimpleJWT",
                "content": """# SimpleJWT Setup

Cài đặt:

```bash
pip install djangorestframework-simplejwt
```

Thêm vào settings:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```
""",
                "author": "charlie",
                "status": "publish",
                "tags": ["django", "rest-api"],
            },
            {
                "title": "[WIP] Bài viết Nháp về PostgreSQL JSONB",
                "content": """# PostgreSQL JSONB

Đây là bài nháp chưa hoàn thành...

JSONB rất mạnh mẽ cho việc lưu dữ liệu linh hoạt.
""",
                "author": "bob",
                "status": "draft",
                "tags": ["postgresql"],
            },
        ]

        posts = []
        for p in posts_data:
            author = users.get(p["author"])
            post, created = Post.objects.get_or_create(
                title=p["title"],
                defaults={
                    "content": p["content"],
                    "author": author,
                    "status": p["status"],
                },
            )
            if created:
                post.tags.set([tags[slug] for slug in p["tags"] if slug in tags])
                self.stdout.write(f"  ✅ Post tạo: {post.title[:50]}")
            else:
                self.stdout.write(f"  ⏭ Post đã tồn tại: {post.title[:50]}")
            posts.append(post)

        # ========== COMMENTS ==========
        published_posts = [p for p in posts if p.status == "publish"]
        comments_data = [
            {"post": published_posts[0], "author": "bob", "content": "Bài viết rất chi tiết và dễ hiểu! Cảm ơn bạn."},
            {"post": published_posts[0], "author": "charlie", "content": "Tôi đã áp dụng vào dự án của mình và hoạt động rất tốt!"},
            {"post": published_posts[1], "author": "alice", "content": "Docker Compose thực sự tiện lợi, cảm ơn đã chia sẻ."},
            {"post": published_posts[1], "author": "charlie", "content": "Bạn có thể thêm phần về nginx không?"},
            {"post": published_posts[2], "author": "bob", "content": "Lỗi N+1 là nguyên nhân phổ biến gây chậm API, bài viết rất hữu ích!"},
            {"post": published_posts[3], "author": "alice", "content": "JWT rất tiện cho API stateless."},
        ]

        for c in comments_data:
            author = users.get(c["author"])
            comment, created = Comment.objects.get_or_create(
                post=c["post"],
                author=author,
                content=c["content"],
            )
            if created:
                self.stdout.write(f"  ✅ Comment tạo: {c['content'][:40]}")

        self.stdout.write(self.style.SUCCESS("\n🎉 Dữ liệu mẫu đã được tạo thành công!"))
        self.stdout.write("\n📝 Tài khoản mẫu:")
        self.stdout.write("  - admin_user / Admin@123456 (Superuser)")
        self.stdout.write("  - alice / Alice@123456")
        self.stdout.write("  - bob / Bob@123456")
        self.stdout.write("  - charlie / Charlie@123456")
        self.stdout.write("\n🔗 Endpoints chính:")
        self.stdout.write("  POST /api/auth/login/    — Đăng nhập lấy JWT")
        self.stdout.write("  GET  /api/posts/         — Danh sách bài viết")
        self.stdout.write("  GET  /api/tags/          — Danh sách tags")
        self.stdout.write("  GET  /api/comments/      — Danh sách bình luận")
        self.stdout.write("  GET  /api/media/         — Media của tôi")
