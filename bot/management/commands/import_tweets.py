import json
import requests
from datetime import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import EvoDevo Papers legacy tweets."

    def handle(self, *args, **options):
        """Read, parse, and import the JSON file with backed-up tweets."""

        self.stdout.write(f"Reading...")

        with open("tweets.js", "r", encoding="utf-8") as f:
            tweets = json.load(f)

            self.stdout.write(f"Found {len(tweets)} tweets.")

            for tweet_data in tweets:
                tweet = tweet_data["tweet"]

                id = tweet["id"]
                created_at = self.get_created_at_datetime(tweet["created_at"])

                url = tweet["entities"]["urls"][0]["url"]
                expanded_url = tweet["entities"]["urls"][0]["expanded_url"]
                full_text = tweet["full_text"]

                # TODO: Resolve short expanded_url to get cleaned_url
                # resolved_url = self.resolve_expanded_url(expanded_url)
                cleaned_text = full_text.replace(url, expanded_url)

                print(id, created_at)
                print(url, expanded_url)
                print(cleaned_text)
                print()

    def get_created_at_datetime(self, created_at):
        """Parse created_at timestamp to datetime object."""
        # Example: "Thu Nov 03 05:19:51 +0000 2022"
        return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")

    def resolve_expanded_url(self, expanded_url):
        """Resolve ift.tt and dlvr.it URLs to their true address."""
        if (
            expanded_url.startswith("http://dlvr.it")
            or expanded_url.startswith("http://ift.tt")
        ):
            response = requests.head(expanded_url, allow_redirects=True, timeout=10)
            return response.url
        else:
            return expanded_url

    def remove_hashtag(self):
        """Remove #evodevo hashtag from full_text."""

    def determine_source_feed_from_expanded_url(self):
        """Discover the source by the paper's URL."""

    def generate_twitter_status_url(self):
        """Build Twitter status URL from tweet ID."""
