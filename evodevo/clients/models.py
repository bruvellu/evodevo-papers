from django.db import models


class Client(models.Model):
    account = models.CharField(max_length=50)
    api_base_url = models.CharField(blank=True, max_length=50)
    client_key = models.CharField(blank=True, max_length=50)
    client_secret = models.CharField(blank=True, max_length=50)
    access_token = models.CharField(blank=True, max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.account
