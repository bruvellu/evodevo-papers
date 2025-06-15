from django.contrib import admin
from django.urls import path
from django_distill import distill_path
from bot.views import home, feeds, feed
from bot.models import Feed

def get_feeds():
    for feed_obj in Feed.objects.all():
        yield {'id': feed_obj.id}

urlpatterns = [
    distill_path('', home, name='home'),
    distill_path('feeds/', feeds, name='feeds'),
    distill_path('feed/<int:id>/', feed, name='feed', distill_func=get_feeds),
    path('admin/', admin.site.urls),
]
