from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import UserProfile, Post, Comment, Follow

# --- SETUP ---

class BaseTestCase(TestCase):
    def setUp(self):
        # Create user1 (alice)
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='testpass123')
        self.profile1 = UserProfile.objects.create(user=self.user1, bio='Alice bio')

        # Create user2 (bob)
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='testpass123')
        self.profile2 = UserProfile.objects.create(user=self.user2, bio='Bob bio')

        # Create clients
        self.client = Client()
        # Create an alternative client for user2 if needed
        self.client2 = Client()


# --- CLASS 1: AuthTests ---

class AuthTests(BaseTestCase):
    def test_register_get(self):
        """GET /register/ returns 200"""
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
        print("AuthTests.test_register_get: OK")

    def test_register_post_success(self):
        """POST valid data to /register/ creates user and redirects to /feed/"""
        # Delete profile1/profile2 just to avoid any constraints if registration creates a new user,
        # but here we register 'charlie' which does not exist yet.
        data = {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password1': 'Securepass123!',
            'password2': 'Securepass123!'
        }
        response = self.client.post(reverse('core:register'), data)
        self.assertRedirects(response, reverse('core:feed'))
        self.assertTrue(User.objects.filter(username='charlie').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='charlie').exists())
        print("AuthTests.test_register_post_success: OK")

    def test_register_post_mismatched_passwords(self):
        """POST mismatched passwords returns form error"""
        data = {
            'username': 'charlie2',
            'email': 'charlie2@example.com',
            'password1': 'Securepass123!',
            'password2': 'Wrongpass123!'
        }
        response = self.client.post(reverse('core:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='charlie2').exists())
        # Check if form errors exist in the template context
        form = response.context['form']
        self.assertTrue(form.errors)
        print("AuthTests.test_register_post_mismatched_passwords: OK")

    def test_login_get(self):
        """GET /login/ returns 200"""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        print("AuthTests.test_login_get: OK")

    def test_login_post_success(self):
        """POST valid credentials redirects to /feed/"""
        data = {
            'username': 'alice',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('core:login'), data)
        self.assertRedirects(response, reverse('core:feed'))
        print("AuthTests.test_login_post_success: OK")

    def test_login_post_wrong_password(self):
        """POST wrong password returns 200 with error"""
        data = {
            'username': 'alice',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('core:login'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        print("AuthTests.test_login_post_wrong_password: OK")

    def test_logout_post(self):
        """POST /logout/ redirects to /login/"""
        # Log in first
        self.client.login(username='alice', password='testpass123')
        response = self.client.post(reverse('core:logout'))
        self.assertRedirects(response, reverse('core:login'))
        print("AuthTests.test_logout_post: OK")


# --- CLASS 2: PostTests ---

class PostTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice', password='testpass123')
        self.post = Post.objects.create(author=self.user1, content='First post content')

    def test_feed_get(self):
        """GET /feed/ returns 200"""
        response = self.client.get(reverse('core:feed'))
        self.assertEqual(response.status_code, 200)
        print("PostTests.test_feed_get: OK")

    def test_create_post_success(self):
        """POST to /post/create/ with content creates a Post object"""
        data = {
            'content': 'Second post content'
        }
        response = self.client.post(reverse('core:create_post'), data)
        self.assertRedirects(response, reverse('core:feed'))
        self.assertEqual(Post.objects.count(), 2)
        print("PostTests.test_create_post_success: OK")

    def test_create_post_empty_content(self):
        """POST to /post/create/ with empty content does NOT create a post"""
        data = {
            'content': ''
        }
        response = self.client.post(reverse('core:create_post'), data)
        self.assertRedirects(response, reverse('core:feed'))
        self.assertEqual(Post.objects.count(), 1)
        print("PostTests.test_create_post_empty_content: OK")

    def test_create_post_too_long(self):
        """POST to /post/create/ with content over 500 chars does NOT create a post"""
        data = {
            'content': 'a' * 501
        }
        response = self.client.post(reverse('core:create_post'), data)
        self.assertRedirects(response, reverse('core:feed'))
        self.assertEqual(Post.objects.count(), 1)
        print("PostTests.test_create_post_too_long: OK")

    def test_feed_contains_post(self):
        """GET /feed/ contains the post content in response"""
        response = self.client.get(reverse('core:feed'))
        self.assertContains(response, 'First post content')
        print("PostTests.test_feed_contains_post: OK")


# --- CLASS 3: LikeTests ---

class LikeTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice', password='testpass123')
        self.post = Post.objects.create(author=self.user1, content='Post to like')

    def test_like_toggle(self):
        """POST to /post/like/<pk>/ toggles like state"""
        # Like
        response = self.client.post(reverse('core:like_toggle', kwargs={'pk': self.post.pk}))
        self.assertEqual(self.post.likes.count(), 1)
        self.assertIn(self.user1, self.post.likes.all())

        # Unlike
        response = self.client.post(reverse('core:like_toggle', kwargs={'pk': self.post.pk}))
        self.assertEqual(self.post.likes.count(), 0)
        self.assertNotIn(self.user1, self.post.likes.all())
        print("LikeTests.test_like_toggle: OK")


# --- CLASS 4: CommentTests ---

class CommentTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice', password='testpass123')
        self.post = Post.objects.create(author=self.user1, content='Post to comment on')

    def test_comment_create_success(self):
        """POST to /comment/<pk>/ with content creates a Comment"""
        data = {
            'content': 'Nice post'
        }
        response = self.client.post(reverse('core:add_comment', kwargs={'pk': self.post.pk}), data)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, 'Nice post')
        print("CommentTests.test_comment_create_success: OK")

    def test_comment_create_empty(self):
        """POST with empty content does NOT create a comment"""
        data = {
            'content': ''
        }
        response = self.client.post(reverse('core:add_comment', kwargs={'pk': self.post.pk}), data)
        self.assertEqual(Comment.objects.count(), 0)
        print("CommentTests.test_comment_create_empty: OK")


# --- CLASS 5: FollowTests ---

class FollowTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice', password='testpass123')

    def test_follow_toggle(self):
        """POST to /follow/<username>/ follows and unfollows"""
        # Follow
        response = self.client.post(reverse('core:follow_toggle', kwargs={'username': 'bob'}))
        self.assertEqual(Follow.objects.count(), 1)
        follow_obj = Follow.objects.first()
        self.assertEqual(follow_obj.follower, self.user1)
        self.assertEqual(follow_obj.following, self.user2)

        # Unfollow
        response = self.client.post(reverse('core:follow_toggle', kwargs={'username': 'bob'}))
        self.assertEqual(Follow.objects.count(), 0)
        print("FollowTests.test_follow_toggle: OK")

    def test_cannot_follow_self(self):
        """Cannot follow yourself: POST to /follow/alice/ does nothing"""
        response = self.client.post(reverse('core:follow_toggle', kwargs={'username': 'alice'}))
        self.assertEqual(Follow.objects.count(), 0)
        print("FollowTests.test_cannot_follow_self: OK")


# --- CLASS 6: FeedTests ---

class FeedTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice', password='testpass123')
        # Alice follows bob
        Follow.objects.create(follower=self.user1, following=self.user2)
        # Bob has 2 posts
        self.post1 = Post.objects.create(author=self.user2, content="Bob first post")
        self.post2 = Post.objects.create(author=self.user2, content="Bob second post")

    def test_feed_content_with_follow(self):
        """GET /feed/ returns 200 and contains both of bob's posts"""
        response = self.client.get(reverse('core:feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bob first post")
        self.assertContains(response, "Bob second post")
        print("FeedTests.test_feed_content_with_follow: OK")

    def test_feed_content_after_unfollow_fallback(self):
        """After alice unfollows bob, GET /feed/ falls back to all posts (since following list is empty)"""
        # Unfollow bob
        Follow.objects.filter(follower=self.user1, following=self.user2).delete()
        response = self.client.get(reverse('core:feed'))
        self.assertEqual(response.status_code, 200)
        # Since following list is empty, it falls back to all posts, showing Bob's posts
        self.assertContains(response, "Bob first post")
        self.assertContains(response, "Bob second post")
        print("FeedTests.test_feed_content_after_unfollow_fallback: OK")


# --- CLASS 7: ProfileTests ---

class ProfileTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='alice', password='testpass123')

    def test_profile_alice(self):
        """GET /profile/alice/ returns 200 and shows Edit Profile"""
        response = self.client.get(reverse('core:profile', kwargs={'username': 'alice'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Profile')
        print("ProfileTests.test_profile_alice: OK")

    def test_profile_bob(self):
        """GET /profile/bob/ returns 200 and shows Follow or Unfollow"""
        response = self.client.get(reverse('core:profile', kwargs={'username': 'bob'}))
        self.assertEqual(response.status_code, 200)
        # Should show follow button since we are logged in as alice and not following bob
        self.assertContains(response, 'Follow')
        print("ProfileTests.test_profile_bob: OK")

    def test_profile_nonexistent(self):
        """GET /profile/nonexistent/ returns 404"""
        response = self.client.get(reverse('core:profile', kwargs={'username': 'nonexistent'}))
        self.assertEqual(response.status_code, 404)
        print("ProfileTests.test_profile_nonexistent: OK")

    def test_profile_edit(self):
        """POST to /profile/edit/ with bio='Hello world' updates alice's UserProfile bio"""
        # Verify edit GET returns 200
        response_get = self.client.get(reverse('core:edit_profile'))
        self.assertEqual(response_get.status_code, 200)

        data = {
            'bio': 'Hello world'
        }
        response = self.client.post(reverse('core:edit_profile'), data)
        self.assertRedirects(response, reverse('core:profile', kwargs={'username': 'alice'}))
        # Refresh from db
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.bio, 'Hello world')
        print("ProfileTests.test_profile_edit: OK")

# Run with: python manage.py test core
# Expected: all tests pass with OK
