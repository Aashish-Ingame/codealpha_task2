from django.urls import path

from .views import (
    AddCommentView,
    CreatePostView,
    EditProfileView,
    FeedView,
    FollowToggleView,
    LikePostView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    UsersListView,
)

app_name = "core"

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Feed
    path("feed/", FeedView.as_view(), name="feed"),

    # Post actions
    path("post/create/", CreatePostView.as_view(), name="create_post"),
    path("post/like/<int:pk>/", LikePostView.as_view(), name="like_toggle"),
    path("comment/<int:pk>/", AddCommentView.as_view(), name="add_comment"),

    # Follow actions
    path("follow/<str:username>/", FollowToggleView.as_view(), name="follow_toggle"),

    # Explore
    path("users/", UsersListView.as_view(), name="users_list"),

    # Profiles — edit must come before <username> to avoid matching "edit" as a username
    path("profile/edit/", EditProfileView.as_view(), name="edit_profile"),
    path("profile/<str:username>/", ProfileView.as_view(), name="profile"),
]
