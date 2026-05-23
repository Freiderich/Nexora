from django.conf import settings
from django.db import models


class Post(models.Model):
    VISIBILITY_PUBLIC = "public"
    VISIBILITY_UNLISTED = "unlisted"
    VISIBILITY_PRIVATE = "private"

    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, "Public"),
        (VISIBILITY_UNLISTED, "Unlisted"),
        (VISIBILITY_PRIVATE, "Private"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    visibility = models.CharField(
        max_length=16, choices=VISIBILITY_CHOICES, default=VISIBILITY_PUBLIC
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment {self.id} on post {self.post_id}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_like")
        ]

    def __str__(self):
        return f"Like {self.id} on post {self.post_id}"


class Reaction(models.Model):
    REACTION_LOVE = "love"
    REACTION_LAUGH = "laugh"
    REACTION_WOW = "wow"
    REACTION_SAD = "sad"
    REACTION_FIRE = "fire"

    REACTION_CHOICES = [
        (REACTION_LOVE, "❤"),
        (REACTION_LAUGH, "😂"),
        (REACTION_WOW, "😮"),
        (REACTION_SAD, "😢"),
        (REACTION_FIRE, "🔥"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reactions"
    )
    kind = models.CharField(max_length=12, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_reaction")
        ]

    def __str__(self):
        return f"Reaction {self.kind} {self.id} on post {self.post_id}"

# Create your models here.
