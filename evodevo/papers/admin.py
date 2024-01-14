from django.contrib import admin
from papers import models


class StatusAdmin(admin.ModelAdmin):

    list_display = ['id', 'text', 'published', 'created_at', 'url']


admin.site.register(models.Status, StatusAdmin)

