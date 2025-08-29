from django.contrib import admin

from . import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ["account", "is_active", "platform", "api_base_url", "access_token"]


class FeedAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_active",
        "source",
        "source__live",
        "source__status_code",
        "source__last_change",
    ]
    readonly_fields = ["modified"]


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "link",
        "entry__source__feed__name",
        "created",
        "is_new",
    ]
    list_filter = ["entry__source__feed__name", "is_new", "created"]
    search_fields = ["title"]
    readonly_fields = ["created", "modified"]
    ordering = ["-created"]


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
    list_filter = ["client__platform", "is_published", "published", "created"]
    search_fields = ["post__title"]
    readonly_fields = ["created", "modified"]


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Feed, FeedAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Status, StatusAdmin)
