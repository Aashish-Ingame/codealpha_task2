from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import EditProfileForm, LoginForm, RegisterForm
from .models import Comment, Follow, Post, UserProfile


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _safe_redirect(request, fallback="/feed/"):
    """Redirect back to the referring page; fall back to /feed/ if unavailable."""
    referer = request.META.get("HTTP_REFERER", "")
    # Only trust same-host referers
    host = request.get_host()
    if referer and host in referer:
        return HttpResponseRedirect(referer)
    return redirect(fallback)


# ─── Auth Views ──────────────────────────────────────────────────────────────

class RegisterView(View):
    """GET: render registration form. POST: create User + UserProfile, login, redirect."""

    template_name = "core/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("core:feed")
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect("core:feed")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    """GET: render login form. POST: authenticate, login, redirect."""

    template_name = "core/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("core:feed")
        return render(request, self.template_name, {"form": LoginForm(request)})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("core:feed")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    """POST only: log the user out and redirect to /login/."""

    def post(self, request):
        logout(request)
        return redirect("core:login")


# ─── Feed View ────────────────────────────────────────────────────────────────

class FeedView(LoginRequiredMixin, View):
    """Main feed — shows posts from followed users + own posts."""

    login_url = "/login/"
    template_name = "core/feed.html"

    def get(self, request):
        following_ids = list(
            Follow.objects.filter(follower=request.user)
            .values_list("following", flat=True)
        )

        if following_ids:
            posts_qs = Post.objects.filter(
                Q(author_id__in=following_ids) | Q(author=request.user)
            )
        else:
            posts_qs = Post.objects.all()

        posts = (
            posts_qs
            .order_by("-created_at")
            .select_related("author", "author__profile")
            .prefetch_related(
                "comments",
                "comments__author",
                "comments__author__profile",
                "likes",
            )
        )

        liked_post_ids = set(request.user.liked_posts.values_list("id", flat=True))

        suggested_users = (
            User.objects.exclude(id=request.user.id)
            .exclude(id__in=following_ids)
            .select_related("profile")[:5]
        )

        follower_count = Follow.objects.filter(following=request.user).count()
        following_count = len(following_ids)

        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            user_profile = None

        return render(request, self.template_name, {
            "posts": posts,
            "liked_post_ids": liked_post_ids,
            "suggested_users": suggested_users,
            "follower_count": follower_count,
            "following_count": following_count,
            "user_profile": user_profile,
        })


# ─── Post Actions ─────────────────────────────────────────────────────────────

class CreatePostView(LoginRequiredMixin, View):
    """POST only — creates a new post and redirects back to feed."""

    login_url = "/login/"

    def post(self, request):
        content = request.POST.get("content", "").strip()
        if content and len(content) <= 500:
            post = Post(author=request.user, content=content)
            if request.FILES.get("image"):
                post.image = request.FILES["image"]
            post.save()
        return redirect("core:feed")


class LikePostView(LoginRequiredMixin, View):
    """POST only — toggles a like on a post. Redirects back to referring page."""

    login_url = "/login/"

    def post(self, request, pk):
        try:
            post = get_object_or_404(Post, id=pk)
        except Http404:
            return _safe_redirect(request)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return _safe_redirect(request)


# Keep the old name as an alias so existing URL references stay valid
LikeToggleView = LikePostView


class AddCommentView(LoginRequiredMixin, View):
    """POST only — adds a comment to a post. Redirects back to referring page."""

    login_url = "/login/"

    def post(self, request, pk):
        try:
            post = get_object_or_404(Post, id=pk)
        except Http404:
            return _safe_redirect(request)
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(post=post, author=request.user, content=content[:300])
        return _safe_redirect(request)


# ─── Follow Actions ───────────────────────────────────────────────────────────

class FollowToggleView(LoginRequiredMixin, View):
    """POST only — follows or unfollows a user. Redirects back to referring page."""

    login_url = "/login/"

    def post(self, request, username):
        try:
            target = get_object_or_404(User, username=username)
        except Http404:
            return _safe_redirect(request)
        if target != request.user:
            existing = Follow.objects.filter(follower=request.user, following=target)
            if existing.exists():
                existing.delete()
            else:
                Follow.objects.create(follower=request.user, following=target)
        return _safe_redirect(request)


# ─── Profile Views ────────────────────────────────────────────────────────────

class ProfileView(LoginRequiredMixin, View):
    """Displays a user's public profile with their posts."""

    login_url = "/login/"
    template_name = "core/profile.html"

    def get(self, request, username):
        try:
            profile_user = get_object_or_404(User, username=username)
        except Http404:
            raise Http404("User not found")

        try:
            user_profile = profile_user.profile
        except UserProfile.DoesNotExist:
            user_profile = None

        follower_count  = Follow.objects.filter(following=profile_user).count()
        following_count = Follow.objects.filter(follower=profile_user).count()
        post_count      = Post.objects.filter(author=profile_user).count()

        is_own_profile = request.user == profile_user
        is_following = (
            not is_own_profile
            and Follow.objects.filter(
                follower=request.user, following=profile_user
            ).exists()
        )

        posts = (
            Post.objects.filter(author=profile_user)
            .order_by("-created_at")
            .select_related("author", "author__profile")
            .prefetch_related("comments", "comments__author", "likes")
        )

        liked_post_ids = set(request.user.liked_posts.values_list("id", flat=True))

        return render(request, self.template_name, {
            "profile_user":   profile_user,
            "user_profile":   user_profile,
            "follower_count": follower_count,
            "following_count": following_count,
            "post_count":     post_count,
            "is_own_profile": is_own_profile,
            "is_following":   is_following,
            "posts":          posts,
            "liked_post_ids": liked_post_ids,
        })


class EditProfileView(LoginRequiredMixin, View):
    """GET: pre-filled bio/avatar form. POST: saves and redirects to own profile."""

    login_url = "/login/"
    template_name = "core/edit_profile.html"

    def _get_or_create_profile(self, user):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return profile

    def get(self, request):
        profile = self._get_or_create_profile(request.user)
        return render(request, self.template_name, {"form": EditProfileForm(instance=profile)})

    def post(self, request):
        profile = self._get_or_create_profile(request.user)
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("core:profile", username=request.user.username)
        return render(request, self.template_name, {"form": form})


# ─── Explore / Users List ─────────────────────────────────────────────────────

class UsersListView(LoginRequiredMixin, View):
    """Lists all users (except self) ordered by popularity \u2014 the Explore page."""

    login_url = "/login/"
    template_name = "core/users.html"

    def get(self, request):
        following_ids = set(
            Follow.objects.filter(follower=request.user)
            .values_list("following", flat=True)
        )

        users = (
            User.objects.exclude(id=request.user.id)
            .select_related("profile")
            .annotate(follower_count=Count("followers", distinct=True))
            .order_by("-follower_count", "username")
        )

        return render(request, self.template_name, {
            "users": users,
            "following_ids": following_ids,
        })

