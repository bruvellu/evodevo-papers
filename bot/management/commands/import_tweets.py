import json
from datetime import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import EvoDevo Papers legacy tweets."

    def handle(self, *args, **options):
        """Read, parse, and import the JSON file with backed-up tweets."""

        with open("tweets.js", "r", encoding="utf-8") as f:
            tweets = json.load(f)

            self.stdout.write(f"Found {len(tweets)} tweets.")

            for tweet_data in tweets:
                tweet = tweet_data["tweet"]

                id = tweet["id"]
                created_at = self.get_created_at_datetime(tweet["created_at"])

                print(id, created_at)
                print(tweet["full_text"])
                print()

    def get_created_at_datetime(self, created_at):
        """Parse created_at timestamp to datetime object."""
        # Example: "Thu Nov 03 05:19:51 +0000 2022"
        return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")

    def replace_shortened_by_expanded_url(self):
        """Replace t.co URL by true expanded URL in the full_text."""

    def remove_hashtag(self):
        """Remove #evodevo hashtag from full_text."""

    def determine_source_feed_from_expanded_url(self):
        """Discover the source by the paper's URL."""

    def generate_twitter_status_url(self):
        """Build Twitter status URL from tweet ID."""
