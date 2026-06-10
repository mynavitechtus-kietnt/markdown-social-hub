"""
posts/tests/test_views.py — Unit test cho Post và Tag API endpoints.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from posts.models import Post, Tag


class PostAPITest(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass@1234")
        self.other_user = User.objects.create_user(
            username="other", password="pass@1234"
        )
        self.tag = Tag.objects.create(name="test-tag", slug="test-tag")
        self.published_post = Post.objects.create(
            title="Public Post Title Here",
            content="This is public post content.",
            author=self.author,
            status=Post.Status.PUBLISH,
        )
        self.draft_post = Post.objects.create(
            title="Draft Post Title Here",
            content="This is a draft post content.",
            author=self.author,
            status=Post.Status.DRAFT,
        )
        self.list_url = reverse("post-list")

    def test_list_posts_anonymous_only_publish(self):
        """Anonymous chỉ thấy bài PUBLISH."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(self.published_post.pk), ids)
        self.assertNotIn(str(self.draft_post.pk), ids)

    def test_create_post_unauthenticated(self):
        """Anonymous không được tạo bài viết."""
        data = {
            "title": "New Post Title",
            "content": "Some content here.",
            "status": "draft",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_authenticated(self):
        """User đăng nhập tạo được bài viết."""
        self.client.force_authenticate(user=self.author)
        data = {
            "title": "My New Post Title",
            "content": "This is the content of my new post.",
            "status": "draft",
            "tag_ids": [self.tag.pk],
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)

    def test_create_post_short_title_fails(self):
        """Tiêu đề quá ngắn thì trả về lỗi 400."""
        self.client.force_authenticate(user=self.author)
        data = {"title": "Hi", "content": "Valid content here.", "status": "draft"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_retrieve_published_post_anonymous(self):
        """Anonymous đọc được bài PUBLISH."""
        url = reverse("post-detail", kwargs={"pk": self.published_post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post_by_owner(self):
        """Chủ sở hữu cập nhật được bài viết."""
        self.client.force_authenticate(user=self.author)
        url = reverse("post-detail", kwargs={"pk": self.published_post.pk})
        data = {
            "title": "Updated Post Title Here",
            "content": "Updated content that is long enough.",
            "status": "publish",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.title, "Updated Post Title Here")

    def test_update_post_by_non_owner_fails(self):
        """User khác không được sửa bài của người khác."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("post-detail", kwargs={"pk": self.published_post.pk})
        data = {
            "title": "Hacked title haha",
            "content": "Hacked content here.",
            "status": "publish",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_by_owner(self):
        """Chủ sở hữu xóa được bài viết."""
        self.client.force_authenticate(user=self.author)
        url = reverse("post-detail", kwargs={"pk": self.draft_post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_post_by_non_owner_fails(self):
        """User khác không xóa được bài của người khác."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("post-detail", kwargs={"pk": self.published_post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_posts_action(self):
        """my-posts chỉ trả bài của user đang đăng nhập."""
        self.client.force_authenticate(user=self.author)
        url = reverse("post-my-posts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)  # cả draft lẫn publish

    def test_publish_action(self):
        """Publish action đổi trạng thái sang publish."""
        self.client.force_authenticate(user=self.author)
        url = reverse("post-publish", kwargs={"pk": self.draft_post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft_post.refresh_from_db()
        self.assertEqual(self.draft_post.status, Post.Status.PUBLISH)

    def test_search_filter(self):
        """Filter tìm kiếm theo từ khóa trong title."""
        url = self.list_url + "?search=Public"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_tag_filter(self):
        """Filter theo slug của tag."""
        self.published_post.tags.add(self.tag)
        url = self.list_url + f"?tag={self.tag.slug}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
