from django.db import models
from django.urls import reverse
from feeds.models import Post as Entry
from feeds.models import Source


class Client(models.Model):
    account = models.CharField(max_length=50)
    api_base_url = models.CharField(blank=True, max_length=50)
    access_token = models.CharField(blank=True, max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.account

# TODO: Add created and modified fields

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

# TODO: Rename created and add modified fields

class Post(models.Model):
    entry = models.ForeignKey(Entry, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(blank=True)
    response = models.TextField(blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    url = models.URLField(blank=True)

    def generate_text(self):
        template = f"{self.entry.title} {self.entry.link} #EvoDevo #Papers"
        self.text = template
        return self.text

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse("post", args=(self.id,))
