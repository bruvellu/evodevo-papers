from django.contrib import admin
from django.urls import path
from django_distill import distill_path
from bot.views import home, feeds, feed

urlpatterns = [
    distill_path('', home, name='home'),
    distill_path('feeds/', feeds, name='feeds'),
    distill_path('feed/<int:id>/', feed, name='feed'),
    path('admin/', admin.site.urls),
]
