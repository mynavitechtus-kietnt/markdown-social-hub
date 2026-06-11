# Markdown Social Hub

API mạng xã hội hỗ trợ Markdown, quản lý Media và cá nhân hóa trải nghiệm người dùng.

## Cài đặt với Docker

```bash
cp .env.example .env
docker-compose up --build
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_data
```

## Endpoints

| Method | URL | Mô tả | Auth |
|--------|-----|-------|------|
| POST | /api/auth/register/ | Đăng ký | ❌ |
| POST | /api/auth/login/ | Đăng nhập (JWT) | ❌ |
| POST | /api/auth/token/refresh/ | Refresh token | ❌ |
| GET/PATCH | /api/auth/profile/ | Hồ sơ cá nhân | ✅ |
| GET | /api/posts/ | Danh sách bài PUBLISH | ❌ |
| POST | /api/posts/ | Tạo bài viết | ✅ |
| GET | /api/posts/{id}/ | Chi tiết bài | ❌ |
| PUT/PATCH | /api/posts/{id}/ | Cập nhật bài | ✅ Owner |
| DELETE | /api/posts/{id}/ | Xóa bài | ✅ Owner |
| GET | /api/posts/my-posts/ | Bài của tôi | ✅ |
| POST | /api/posts/{id}/publish/ | Publish bài | ✅ Owner |
| POST | /api/posts/{id}/draft/ | Draft bài | ✅ Owner |
| GET | /api/tags/ | Danh sách tags | ❌ |
| POST | /api/tags/ | Tạo tag | ✅ |
| GET | /api/media/ | Media của tôi | ✅ |
| POST | /api/media/ | Upload ảnh | ✅ |
| DELETE | /api/media/{id}/ | Xóa media | ✅ Owner |
| GET | /api/comments/ | Danh sách comments | ❌ |
| POST | /api/comments/ | Tạo comment | ✅ |
| DELETE | /api/comments/{id}/ | Xóa comment | ✅ Owner |

## Tài khoản mẫu

| Username | Password | Role |
|----------|----------|------|
| admin_user | Admin@123456 | Superuser |
| alice | Alice@123456 | Thành viên |
| bob | Bob@123456 | Thành viên |
| charlie | Charlie@123456 | Thành viên |

## Test

```bash
python manage.py test
coverage run manage.py test && coverage report
```
