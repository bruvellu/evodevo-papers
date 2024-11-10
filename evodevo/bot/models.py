from django.db import models
from feeds.models import Source


class Client(models.Model):
    account = models.CharField(max_length=50)
    api_base_url = models.CharField(blank=True, max_length=50)
    access_token = models.CharField(blank=True, max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.account


class Feed(models.Model):
    name = models.CharField(max_length=100)
    source = models.OneToOneField(Source, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
