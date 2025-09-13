import json
import time

from atproto import Client as ATClient
from atproto import client_utils
from django.db import models
from django.urls import reverse
from django.utils import timezone
from feeds.models import Post as Entry
from feeds.models import Source
from mastodon import Mastodon


class Client(models.Model):
    platform = models.CharField(blank=True, max_length=50)
    account = models.CharField(max_length=50)
    api_base_url = models.CharField(blank=True, max_length=50)
    access_token = models.CharField(blank=True, max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.account

    @property
    def handle(self):
        """Return account without the @."""
        return self.account[1:]


class Feed(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(default=timezone.now, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    source = models.OneToOneField(
        Source, blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("feed", args=(self.id,))


class Post(models.Model):
    # TODO: Add a foreign key to Feed
    # TODO: Add other relevant fields from Entry
    # TODO: Post information should be independent of Entry
    entry = models.OneToOneField(
        Entry, blank=True, null=True, on_delete=models.SET_NULL
    )
    title = models.TextField(blank=True)
    link = models.URLField(blank=True)
    feed = models.ForeignKey(Feed, blank=True, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(default=timezone.now, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return f'[{self.id}] "{self.title[:50]}..."'

    def get_absolute_url(self):
        return reverse("post", args=(self.id,))

    def get_or_create_statuses(self):
        for client in Client.objects.filter(is_active=True):
            status, created = Status.objects.get_or_create(post=self, client=client)
            status.save()

    def update_is_new(self):
        if self.has_published_statuses():
            self.is_new = False
            self.save()

    def has_published_statuses(self):
        published_statuses = self.statuses.values_list("is_published", flat=True)
        if True in published_statuses:
            return True
        else:
            return False

    @property
    def display_text(self):
        return f"{self.title} {self.link}"


class Status(models.Model):
    # TODO: Remove blank and null for post
    post = models.ForeignKey(
        Post, blank=True, null=True, on_delete=models.CASCADE, related_name="statuses"
    )
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True)
    response = models.JSONField(blank=True, default=dict)
    url = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f'[{self.id}] [{self.client}] "{self.text[:50]}..."'

    def build_text(self, facets=False):
        # Faceted text object required for Bluesky
        text = (
            client_utils.TextBuilder()
            .text(f"{self.post.title}")
            .text(" ")
            .link(f"{self.post.link}", f"{self.post.link}")
            .text(" ")
            .tag("#EvoDevo", "EvoDevo")
        )
        if facets:
            return text
        return text.build_text()

    def publish(self):
        if not self.client.is_active:
            print(
                f"Refusing to publish. Client account is inactive: {self.client.account}"
            )
            return False
        elif self.is_published:
            print(
                f"Refusing to publish. Status already published: {self.client.account}"
            )
            return False
        elif self.client.is_active and not self.is_published:
            published = self.post_to_current_client()
            if published:
                return True
            return False
        else:
            print("Unexpected condition; shouldn't happen.")
            print(f"{self}")
            print(f"{self.client}")
            print(f"{self.post}")
            return False

    def post_to_current_client(self):
        if self.client.platform == "Mastodon":
            posted = self.post_to_mastodon()
        elif self.client.platform == "Bluesky":
            posted = self.post_to_bluesky()
        else:
            print(f"Unsupported platform: {self.client.platform}")
            return False

        if posted:
            return True
        return False

    def login_mastodon(self):
        if not hasattr(self, "mastodon"):
            self.mastodon = Mastodon(
                access_token=self.client.access_token,
                api_base_url=self.client.api_base_url,
            )
            print(f"Logged to {self.client.account}")
        else:
            print(f"Already logged to {self.client.account}")

    def post_to_mastodon(self):
        try:
            self.login_mastodon()
            response = self.mastodon.status_post(
                self.build_text(), visibility="public", language="en"
            )
            self.response = json.loads(response.to_json())["_mastopy_data"]
            self.url = response.url
            self.published = response.created_at
            self.is_published = True
            self.save()
            return True
        except Exception as e:
            print(f"Failed posting to {self.client.account}: {str(e)}")
            return False

    def login_bluesky(self):
        if not hasattr(self, "bluesky"):
            self.bluesky = ATClient()
            self.bluesky.login(self.client.handle, self.client.access_token)
            print(f"Logged to {self.client.account}")
        else:
            print(f"Already logged to {self.client.account}")

    def post_to_bluesky(self):
        try:
            self.login_bluesky()
            response = self.bluesky.send_post(self.build_text(facets=True))
            post = self.get_bluesky_post_info(response.uri)
            if post:
                print(f"Fetched Bluesky post info from uri={response.uri}")
                self.response = post.dict()
                self.url = self.bluesky_uri_to_url(post.uri)
                self.published = post.record.created_at
            else:
                print(f"Failed to fetch Bluesky post info from uri={response.uri}")
                self.response = response.dict()
                self.url = self.bluesky_uri_to_url(response.uri)
                self.published = timezone.now()
            self.is_published = True
            self.save()
            return True
        except Exception as e:
            print(f"Failed posting to {self.client.account}: {str(e)}")
            return False

    def get_bluesky_post_info(self, uri):
        # Avoid racing condition when getting Bluesky post info
        time.sleep(1)
        posts = self.bluesky.get_posts([uri])
        if posts.posts:
            return posts.posts[0]
        time.sleep(3)
        posts = self.bluesky.get_posts([uri])
        if posts.posts:
            return posts.posts[0]
        return None

    def bluesky_uri_to_url(self, uri):
        """Convert Bluesky URI to URL.

        uri = 'at://did:plc:mmwzw6nx4yuwuctagowcievd/app.bsky.feed.post/3ltc4hqycjy2k'
        url = 'https://bsky.app/profile/evodevo-papers.bsky.social/post/3ltc4hqycjy2k'
        """
        import re

        match = re.match(r"at://[^/]+/app\.bsky\.feed\.post/([^/]+)", uri)
        if not match:
            raise ValueError("Invalid URI format")
        post_id = match.group(1)
        return f"https://bsky.app/profile/{self.client.handle}/post/{post_id}"

    def save(self, *args, **kwargs):
        if not self.is_published:
            self.text = self.build_text()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "statuses"
        constraints = [
            models.UniqueConstraint(
                fields=["post", "client"], name="unique_status_per_post_client"
            )
        ]
