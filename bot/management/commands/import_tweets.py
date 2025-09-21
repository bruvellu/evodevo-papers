import json
import os
import time
from datetime import datetime

import requests
from django.core.management.base import BaseCommand

from bot.models import Feed, Post


class Command(BaseCommand):
    help = "Import legacy tweets to EvoDevo Papers database."

    def handle(self, *args, **options):
        """Read processed tweets and create posts."""

        # Read file of processed tweets
        processed_tweets_file = "processed_tweets.json"
        self.stdout.write(f"Reading {processed_tweets_file}...")
        if os.path.exists(processed_tweets_file):
            with open(processed_tweets_file, "r", encoding="utf-8") as f:
                processed_tweets = json.load(f)
        else:
            processed_tweets = {}
        self.stdout.write(f"Found {len(processed_tweets)} tweets.")

        # Create dictionary for import
        posts = {}
        duplicates = 0

        # Loop over processed tweets
        for tweet_id, tweet in processed_tweets.items():
            if tweet["url_status_code"] == 404:
                continue

            # Define values for new post object
            post = {
                "entry": None,
                "feed": self.discover_feed_from_link(tweet["final_link"]),
                "title": tweet["final_title"],
                "link": tweet["final_link"],
                "created": self.get_created_at_datetime(tweet["created_at"]),
                "is_new": True,
            }

            # Skip duplicate posts
            if self.has_duplicate(post, posts):
                print()
                print("DUPLICATE", tweet["id"], tweet["created_at"])
                print(tweet["final_title"])
                print(tweet["final_link"])
                duplicates += 1
                continue

            # Add post to be imported
            posts[tweet_id] = post

        # Print stats
        print()
        print(f"Posts: {len(posts.keys())}")
        print(f"Duplicates: {duplicates}")

    def get_created_at_datetime(self, created_at):
        """Parse created_at timestamp to datetime object."""
        # Example: "Thu Nov 03 05:19:51 +0000 2022"
        return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")

    def discover_feed_from_link(self, link):
        """Discover the Feed object from the paper's link."""
        if link.startswith("https://pubmed") or link.startswith("https://pmc"):
            return Feed.objects.get(name="PubMed")
        elif link.startswith("https://evodevojournal.biomedcentral.com"):
            return Feed.objects.get(name="EvoDevo")
        elif link.startswith("https://www.biorxiv.org"):
            return Feed.objects.get(name="bioRxiv")
        elif link.startswith("https://link.springer.com"):
            return Feed.objects.get(name="Development Genes and Evolution")
        elif link.startswith("https://onlinelibrary.wiley.com/doi/abs/10.1111/ede"):
            return Feed.objects.get(name="Evolution & Development")
        elif link.startswith("https://onlinelibrary.wiley.com/doi/abs/10.1002/jez"):
            return Feed.objects.get(name="Journal of Experimental Zoology Part B")
        elif link.startswith("https://www.frontiersin.org"):
            return Feed.objects.get(name="Frontiers in Ecology and Evolution")

    def generate_twitter_status_url(self):
        """Build Twitter status URL from tweet ID."""

    def has_duplicate(self, entry, posts):
        """Check for duplicated entries before importing."""
        for key, value in posts.items():
            if (
                entry["title"] == value["title"]
                and entry["link"] == value["link"]
            ):
                return True
        return False
