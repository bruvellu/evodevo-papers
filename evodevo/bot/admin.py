from django.contrib import admin
from . import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ['account', 'is_active', 'access_token']


class FeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'source']


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Feed, FeedAdmin)
