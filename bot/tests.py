from django.test import Client, TestCase


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
