from django.contrib import admin
from . import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ["platform", "account", "is_active", "access_token"]


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
    list_display = ["id", "entry__title", "created"]
    readonly_fields = ["created", "modified"]


class StatusAdmin(admin.ModelAdmin):
    list_display = ["id","post__entry__title", "client__platform", "url", "created", "published"]
    readonly_fields = ["created", "modified"]


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Feed, FeedAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Status, StatusAdmin)
