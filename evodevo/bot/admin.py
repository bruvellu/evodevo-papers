from django.contrib import admin
from . import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ["account", "is_active", "access_token"]


class FeedAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "source",
        "source__live",
        "source__status_code",
        "source__last_change",
    ]
    readonly_fields = ['modified']


class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "text", "published", "created", "url"]
    readonly_fields = ['modified']


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Feed, FeedAdmin)
admin.site.register(models.Post, PostAdmin)
