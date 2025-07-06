from django.contrib import admin
from . import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ["account", "is_active", "platform", "api_base_url", "access_token"]


class FeedAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "source",
        "source__live",
        "source__status_code",
        "source__last_change",
    ]
    readonly_fields = ["modified"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created"]
    readonly_fields = ["created", "modified"]


class StatusAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "post__title",
        "client__platform",
        "url",
        "created",
        "published",
        "is_published",
    ]
    readonly_fields = ["created", "modified"]


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Feed, FeedAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Status, StatusAdmin)
