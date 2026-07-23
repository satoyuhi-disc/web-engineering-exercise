from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Post


class PostListViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="alice", password="pw12345!")
        Post.objects.create(title="First post", content="Hello world", author=self.author)
        Post.objects.create(title="Second post", content="Another one", author=self.author)

    def test_home_page_lists_posts_newest_first(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        titles = [p.title for p in response.context["page_obj"]]
        self.assertEqual(titles, ["Second post", "First post"])

    def test_search_filters_by_title(self):
        response = self.client.get(reverse("blog:post_list"), {"q": "First"})
        titles = [p.title for p in response.context["page_obj"]]
        self.assertEqual(titles, ["First post"])

    def test_author_posts_page(self):
        response = self.client.get(reverse("blog:author_posts", args=["alice"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First post")


class PostCreateViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="bob", password="pw12345!")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_authenticated_user_can_create_post(self):
        self.client.login(username="bob", password="pw12345!")
        response = self.client.post(
            reverse("blog:post_create"),
            {"title": "My new post", "content": "Some content"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title="My new post", author=self.author).exists())


class SignUpViewTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("blog:signup"),
            {"username": "carol", "password1": "S0mePassw0rd!", "password2": "S0mePassw0rd!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="carol").exists())
