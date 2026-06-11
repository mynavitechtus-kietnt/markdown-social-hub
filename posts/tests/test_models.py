"""
posts/tests/test_models.py — Unit test cho Post và Tag models.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from posts.models import Post, Tag


class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="python", slug="python")

    def test_str_representation(self):
        self.assertEqual(str(self.tag), "python")

    def test_unique_slug(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="python2", slug="python")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.tag = Tag.objects.create(name="django", slug="django")
        self.post = Post.objects.create(
            title="Hello World Post",
            content="This is a sample content for testing.",
            author=self.user,
            status=Post.Status.DRAFT,
        )
        self.post.tags.add(self.tag)

    def test_str_representation(self):
        self.assertIn("Hello World Post", str(self.post))

    def test_default_status_is_draft(self):
        post = Post.objects.create(
            title="Another post title",
            content="Another content body here.",
            author=self.user,
        )
        self.assertEqual(post.status, Post.Status.DRAFT)

    def test_author_relationship(self):
        self.assertEqual(self.post.author, self.user)

    def test_tag_many_to_many(self):
        self.assertIn(self.tag, self.post.tags.all())

    def test_uuid_primary_key(self):
        import uuid
        self.assertIsInstance(self.post.pk, uuid.UUID)
