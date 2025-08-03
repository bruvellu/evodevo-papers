from django.core.management import load_command_class
from django.test import Client, TestCase

from bot.models import Post


class ViewsTestCase(TestCase):
    """Test cases for all views in the application."""

    fixtures = [
        "posts.json",
        "entries.json",
        "sources.json",
        "feeds.json",
        "statuses.json",
        "clients.json",
    ]

    def setUp(self):
        """Set up test data for all view tests."""
        self.client = Client()

    def test_home_view_renders_successfully(self):
        """Test that the home view renders without errors."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "feeds")
        self.assertContains(response, "posts")

    def test_about_view_renders_successfully(self):
        """Test that the about view renders without errors."""
        response = self.client.get("/about/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "about")
        self.assertIsNotNone(response.context)

    def test_feeds_view_renders_successfully(self):
        """Test that the feeds view renders without errors."""
        response = self.client.get("/feeds/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "feeds")

    def test_posts_view_renders_successfully(self):
        """Test that the posts view renders without errors."""
        response = self.client.get("/posts/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "posts")


class CreatePostsTestCase(TestCase):
    """Test cases for createposts management command."""

    fixtures = [
        "posts.json",
        "entries.json",
        "sources.json",
        "feeds.json",
        "statuses.json",
        "clients.json",
    ]

    def setUp(self):
        """Set up test data for all view tests."""
        self.cmd = load_command_class("bot", "createposts")

    def test_exclude_entries_with_existing_posts(self):
        """Entries with existing posts should NOT be in new_entries."""

        # Remove a post to have an entry without a post (new entry)
        Post.objects.order_by("?").first().delete()

        # Run new entries function a test for existing posts
        new_entries = self.cmd.get_new_entries()
        new_entries_with_post = Post.objects.filter(entry__in=new_entries)
        self.assertFalse(
            new_entries_with_post.exists(),
            f"These entries already have a Post: {[post.entry_id for post in new_entries_with_post]}",
        )

    def test_entry_order_by_created_date(self):
        """Entries should be ordered by 'created' datetime ascending."""
        # Remove three random posts to have new entries for testing
        random_ids = list(Post.objects.order_by("?").values_list("id", flat=True)[:3])
        Post.objects.filter(id__in=random_ids).delete()

        # Test order created
        entries = list(self.cmd.get_new_entries())
        created_list = [e.created for e in entries]
        self.assertEqual(created_list, sorted(created_list))

    def test_exclude_entries_with_filtered_terms(self):
        """Entries whose titles contain filtered terms should NOT be in new_entries."""
        filtered_terms = self.cmd.FILTERED_TITLE_TERMS

        # Add filtered term to entry title and remove post to have a new entry
        post = Post.objects.order_by("?").first()
        modified_title = f"{filtered_terms[0].capitalize()} {post.title}"
        post.entry.title = modified_title
        post.entry.save()
        post.delete()

        new_entries = self.cmd.get_new_entries()
        filtered_entries = self.cmd.filter_entries(new_entries)

        for entry in filtered_entries:
            self.assertFalse(
                any(term.lower() in entry.title.lower() for term in filtered_terms),
                f"[{entry.id}] Entry's title '{entry.title}' should have been filtered out.",
            )
