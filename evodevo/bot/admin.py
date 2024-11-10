from django.contrib import admin
from . import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ['account', 'is_active', 'access_token']


admin.site.register(models.Client, ClientAdmin)
