from django.contrib import admin
from django.urls import path
from django_distill import distill_path
from bot.views import home

urlpatterns = [
    distill_path('', home, name='home'),
    path('admin/', admin.site.urls),
]
