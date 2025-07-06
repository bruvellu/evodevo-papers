from django.db import models
from django.urls import reverse
from feeds.models import Post as Entry
from feeds.models import Source
import json

from mastodon import Mastodon
from atproto import Client as ATClient
from atproto import client_utils


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
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    source = models.OneToOneField(
        Source, blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("feed", args=(self.id,))


class Post(models.Model):
    entry = models.OneToOneField(Entry, blank=True, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    title = models.TextField(blank=True)
    link = models.URLField(blank=True)

    def __str__(self):
        return f"[{self.id}] \"{self.entry.title[:50]}...\""

    def get_absolute_url(self):
        return reverse("post", args=(self.id,))

    def get_or_create_statuses(self):
        for client in Client.objects.filter(is_active=True):
            status, created = Status.objects.get_or_create(post=self, client=client)
            status.save()

    @property
    def display_text(self):
        return f"{self.title} {self.link}"


class Status(models.Model):
    post = models.ForeignKey(
        Post, blank=True, null=True, on_delete=models.SET_NULL, related_name="statuses"
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
        return f"[{self.id}] [{self.client}] \"{self.post.title[:50]}...\""

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
        if not self.is_published:
            try:
                if self.client.platform == "Mastodon":
                    self.post_to_mastodon()
                elif self.client.platform == "Bluesky":
                    self.post_to_bluesky()
                print(f"Published to {self.client.account}")
                return True
            except Exception as e:
                print(f"Failed publishing to {self.client.account}: {str(e)}")
                return False

    def post_to_mastodon(self):
        mastodon = Mastodon(
            access_token=self.client.access_token, api_base_url=self.client.api_base_url
        )
        response = mastodon.status_post(
            self.build_text(), visibility="unlisted", language="en"
        )
        # TODO: Fetch account follower count
        # TODO: Fetch post stats (likes, reposts, etc.)
        self.response = json.loads(response.to_json())["_mastopy_data"]
        self.url = response.url
        self.published = response.created_at
        self.is_published = True
        self.save()

    def post_to_bluesky(self):
        bluesky = ATClient()
        # TODO: Fetch profile follower count
        profile = bluesky.login(self.client.handle, self.client.access_token)
        response = bluesky.send_post(self.build_text(facets=True))
        posts = bluesky.get_posts([response.uri])
        post = posts.posts[0]
        # TODO: Fetch post stats (likes, reposts, etc.)
        self.response = post.dict()
        self.url = self.bluesky_uri_to_url(post.uri)
        self.published = post.record.created_at
        self.is_published = True
        self.save()

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
