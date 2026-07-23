from django.conf import settings
from django.db import models
from django.urls import reverse


class Post(models.Model):
    """A single blog post written by an authenticated user (author)."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.author})"

    def get_absolute_url(self) -> str:
        return reverse("blog:post_detail", args=[self.pk])
