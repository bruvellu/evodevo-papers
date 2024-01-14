from django.contrib import admin
from clients import models


class ClientAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Client, ClientAdmin)

