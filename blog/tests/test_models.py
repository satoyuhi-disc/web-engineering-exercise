from django.contrib.auth.models import User
from django.test import TestCase

from blog.models import Post


class PostModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="alice", password="pw12345!")

    def test_str_returns_title_and_author(self):
        post = Post.objects.create(title="Hello", content="World", author=self.author)
        self.assertEqual(str(post), "Hello (alice)")

    def test_default_ordering_is_newest_first(self):
        older = Post.objects.create(title="Older", content="...", author=self.author)
        newer = Post.objects.create(title="Newer", content="...", author=self.author)
        self.assertEqual(list(Post.objects.all()), [newer, older])

    def test_get_absolute_url(self):
        post = Post.objects.create(title="Hello", content="World", author=self.author)
        self.assertEqual(post.get_absolute_url(), f"/posts/{post.pk}/")
