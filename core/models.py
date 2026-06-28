from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended profile information for each User."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Post(models.Model):
    """A piece of content shared by a user."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to="posts/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at:%Y-%m-%d %H:%M}"


class Comment(models.Model):
    """A comment on a Post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"


class Follow(models.Model):
    """Tracks a follower → following relationship between two Users."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"
