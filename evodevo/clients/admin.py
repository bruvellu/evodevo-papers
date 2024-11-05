from django.contrib import admin
from clients import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ['account', 'is_active', 'client_key', 'client_secret', 'access_token']


admin.site.register(models.Client, ClientAdmin)

