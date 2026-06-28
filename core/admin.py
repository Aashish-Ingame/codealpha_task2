from django.contrib import admin

from .models import Comment, Follow, Post, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email", "bio")
    readonly_fields = ("created_at",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at", "like_count")
    list_filter = ("created_at",)
    search_fields = ("author__username", "content")
    readonly_fields = ("created_at",)
    filter_horizontal = ("likes",)

    @admin.display(description="Likes")
    def like_count(self, obj):
        return obj.likes.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("author__username", "content")
    readonly_fields = ("created_at",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "following__username")
    readonly_fields = ("created_at",)
