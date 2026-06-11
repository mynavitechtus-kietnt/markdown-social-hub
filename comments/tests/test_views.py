"""
comments/tests/test_views.py — Unit test cho Comment API.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from posts.models import Post
from comments.models import Comment


class CommentAPITest(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="post_author", password="pass@1234")
        self.commenter = User.objects.create_user(username="commenter", password="pass@1234")
        self.other = User.objects.create_user(username="other", password="pass@1234")
        self.post = Post.objects.create(
            title="Public Post For Comments",
            content="Content for testing comments here.",
            author=self.author,
            status=Post.Status.PUBLISH,
        )
        self.draft_post = Post.objects.create(
            title="Draft Post Not Commentable",
            content="Draft content here.",
            author=self.author,
            status=Post.Status.DRAFT,
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.commenter,
            content="This is a test comment.",
        )
        self.list_url = reverse("comment-list")

    def test_list_comments_anonymous(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment_authenticated(self):
        self.client.force_authenticate(user=self.commenter)
        data = {"post": str(self.post.pk), "content": "Great article!"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_on_draft_fails(self):
        """Không thể comment trên bài draft."""
        self.client.force_authenticate(user=self.commenter)
        data = {"post": str(self.draft_post.pk), "content": "Trying to comment on draft."}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_own_comment(self):
        """Tác giả comment xóa được comment của mình."""
        self.client.force_authenticate(user=self.commenter)
        url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_comment_fails(self):
        """User khác không xóa được comment của người khác."""
        self.client.force_authenticate(user=self.other)
        url = reverse("comment-detail", kwargs={"pk": self.comment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_post(self):
        """Filter comment theo post id."""
        url = self.list_url + f"?post={self.post.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
