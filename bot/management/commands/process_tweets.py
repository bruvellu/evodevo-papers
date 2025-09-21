import json
import os
import time
from datetime import datetime

import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Parse and process legacy tweets from EvoDevo Papers."

    def handle(self, *args, **options):
        """Read, parse, and import the JSON file with backed-up tweets."""

        # Define input/output files and open
        input_tweets = "tweets.json"
        output_tweets = "processed_tweets.json"
        status_codes = {}

        # Import already processed tweets
        if os.path.exists(output_tweets):
            with open(output_tweets, "r", encoding="utf-8") as f:
                processed_tweets = json.load(f)
        else:
            processed_tweets = {}

        # Import legacy tweets
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
                "url_response_ok": "",
                "url_status_code": "",
                "final_link": "",
                "final_title": "",
            }
            tweet_tmp = processed_tweets[tweet_out["id"]]

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

            # Remove #evodevo hashtag from original text
            text_no_hashtag = self.replace_string(
                tweet_out["original_text"], " #evodevo", ""
            )
            # Remove original URL from text without hashtag
            tweet_out["final_title"] = self.replace_string(
                text_no_hashtag, f' {tweet_out["original_url"]}', ""
            )

            # Replace the original URL with the resolved URL
            if tweet_out["resolved_url"]:
                tweet_out["final_link"] = tweet_out["resolved_url"]

            # Add tweet by ID
            processed_tweets[tweet_out["id"]] = tweet_out

            # Count status codes
            if tweet_out["url_status_code"] in status_codes.keys():
                status_codes[tweet_out["url_status_code"]] += 1
            else:
                status_codes[tweet_out["url_status_code"]] = 1

            # Check shortened titles with ellipsis
            # if "…" in tweet_out["original_text"]:
            # print()
            # print(tweet_out["id"], tweet_out["created_at"])
            # print(f"{tweet_out["final_title"]} {tweet_out["final_link"]} #EvoDevo")

            # Print out processed tweets for reference
            print()
            print(tweet_out["id"], tweet_out["created_at"])
            print(f"{tweet_out["final_title"]} {tweet_out["final_link"]} #EvoDevo")

            # Write out processed tweets for persistent archive
            with open(output_tweets, "w", encoding="utf-8") as f:
                json.dump(processed_tweets, f, ensure_ascii=False, indent=2)

        # Summarize status codes
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
        # Add delay to not overwhelm servers...
        time.sleep(1)
        return requests.head(url, allow_redirects=True, timeout=10)

    def replace_string(self, text, old, new):
        """Replace string in text."""
        return text.replace(old, new)
