import json
import os
import time
from datetime import datetime

import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import EvoDevo Papers legacy tweets."

    def handle(self, *args, **options):
        """Read, parse, and import the JSON file with backed-up tweets."""

        # Define input/output files and open
        input_tweets = "tweets.js"
        output_tweets = "processed_tweets.json"
        status_codes = {}

        if os.path.exists(output_tweets):
            with open(output_tweets, "r", encoding="utf-8") as f:
                processed_tweets = json.load(f)
        else:
            processed_tweets = {}

        self.stdout.write(f"Reading {input_tweets}...")

        with open(input_tweets, "r", encoding="utf-8") as f:
            tweets = json.load(f)

        self.stdout.write(f"Found {len(tweets)} tweets.")

        # Sort tweets by creation date for consistency
        sorted_tweets = sorted(
            tweets,
            key=lambda entry: self.get_created_at_datetime(
                entry["tweet"]["created_at"]
            ),
        )

        # Loop over sorted tweets
        for entry in sorted_tweets:
            # Tweet object with variables to parse and process
            tweet_in = entry["tweet"]
            tweet_out = {
                "id": tweet_in["id"],
                "created_at": tweet_in["created_at"],
                "original_url": tweet_in["entities"]["urls"][0]["url"],
                "expanded_url": tweet_in["entities"]["urls"][0]["expanded_url"],
                "original_text": tweet_in["full_text"],
                "resolved_url": "",
                "cleaned_url": "",
                "url_response_ok": "",
                "url_status_code": "",
                "updated_text": "",
            }
            tweet_tmp = processed_tweets[tweet_out["id"]]

            print()
            print(tweet_out["id"], tweet_out["created_at"])

            # Remove #evodevo hashtag from original text
            tweet_out["updated_text"] = self.replace_string(
                tweet_out["original_text"], " #evodevo", ""
            )

            # Resolve short URL stored as expanded_url
            if not tweet_tmp["resolved_url"] or tweet_tmp["url_status_code"] == 404:
                print(f"Resolving... {tweet_out['expanded_url']}")
                response = self.resolve_url(tweet_out["expanded_url"])
                tweet_out["resolved_url"] = response.url
                tweet_out["url_status_code"] = response.status_code
                tweet_out["url_response_ok"] = response.ok
            else:
                tweet_out["resolved_url"] = tweet_tmp["resolved_url"]
                tweet_out["url_status_code"] = tweet_tmp["url_status_code"]
                tweet_out["url_response_ok"] = tweet_tmp["url_response_ok"]

            # Replace the original URL with the resolved URL
            if tweet_out["resolved_url"]:
                tweet_out["updated_text"] = self.replace_string(
                    tweet_out["updated_text"],
                    tweet_out["original_url"],
                    tweet_out["resolved_url"],
                )

            print(f"Old: {tweet_out["original_text"]}")
            print(f"New: {tweet_out["updated_text"]}")

            processed_tweets[tweet_out["id"]] = tweet_out

            if tweet_out["url_status_code"] in status_codes.keys():
                status_codes[tweet_out["url_status_code"]] += 1
            else:
                status_codes[tweet_out["url_status_code"]] = 1

            # created_at = self.get_created_at_datetime(tweet["created_at"])

            # Write out processed tweets for persistent archive
            with open(output_tweets, "w", encoding="utf-8") as f:
                json.dump(processed_tweets, f, ensure_ascii=False, indent=2)

        print()
        print("Status codes")
        for k, v in status_codes.items():
            print(f"{k}: {v}")

    def get_created_at_datetime(self, created_at):
        """Parse created_at timestamp to datetime object."""
        # Example: "Thu Nov 03 05:19:51 +0000 2022"
        return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")

    def resolve_url(self, url):
        """Resolve URLs to their true address and get status."""
        # Add delay not to overwhelm servers...
        time.sleep(1)
        return requests.head(url, allow_redirects=True, timeout=10)

    def replace_string(self, text, old, new):
        """Replace string in text."""
        return text.replace(old, new)

    def determine_source_feed_from_expanded_url(self):
        """Discover the source by the paper's URL."""

    def generate_twitter_status_url(self):
        """Build Twitter status URL from tweet ID."""
