from django.db import models
from django.urls import reverse
from feeds.models import Post as Entry
from feeds.models import Source

# from atproto import Client as ATClient
from atproto import client_utils


class Client(models.Model):
    platform = models.CharField(blank=True, max_length=50)
    account = models.CharField(max_length=50)
    api_base_url = models.CharField(blank=True, max_length=50)
    access_token = models.CharField(blank=True, max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.account


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
    entry = models.ForeignKey(Entry, blank=True, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    # Deprecated. Use only entry.title and entry.link
    text = models.TextField(blank=True)
    # Deprecated. Response stays with Status
    response = models.TextField(blank=True)
    # Deprecated. Published stays with Status
    published = models.BooleanField(default=False)
    # Deprecated. Published stays with Status
    url = models.URLField(blank=True)

    def __str__(self):
        return f"Post[{self.id}]: {self.entry.title[:30]}..."

    def get_absolute_url(self):
        return reverse("post", args=(self.id,))

    def get_or_create_statuses(self):
        for client in Client.objects.filter(is_active=True):
            status, created = Status.objects.get_or_create(post=self, client=client)
            status.save()

    @property
    def display_text(self):
        return f"{self.entry.title} {self.entry.link} ({ self.entry.source.feed })"


class Status(models.Model):
    post = models.ForeignKey(
        Post, blank=True, null=True, on_delete=models.SET_NULL, related_name="statuses"
    )
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True)
    response = models.JSONField(blank=True)
    url = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "statuses"
        constraints = [
            models.UniqueConstraint(
                fields=["post", "client"], name="unique_status_per_client_post"
            )
        ]

    def __str__(self):
        return f"Status[{self.id}]: {self.post.entry.title[:30]}..."

    def build_text(self, facets=False):
        # Build faceted text object (required for Bluesky)
        text = (
            client_utils.TextBuilder()
            .text(f"{self.post.entry.title}")
            .text(" ")
            .link(f"{self.post.entry.link}", f"{self.post.entry.link}")
            .text(" ")
            .tag("#EvoDevo", "EvoDevo")
        )
        # Return object
        if facets:
            return text
        # Or plain text
        return text.build_text()
