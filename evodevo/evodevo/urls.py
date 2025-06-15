from django.contrib import admin
from django.urls import path
from django_distill import distill_path
from bot.views import home, feeds, feed, posts, post
from bot.models import Feed, Post


def get_feeds():
    for feed_obj in Feed.objects.all():
        yield {"id": feed_obj.id}


def get_posts():
    for post_obj in Post.objects.all():
        yield {"id": post_obj.id}


urlpatterns = [
    distill_path("", home, name="home"),
    distill_path("feeds/", feeds, name="feeds"),
    distill_path("feed/<int:id>/", feed, name="feed", distill_func=get_feeds),
    distill_path("posts/", posts, name="posts"),
    distill_path("post/<int:id>/", post, name="post", distill_func=get_posts),
    path("admin/", admin.site.urls),
]
