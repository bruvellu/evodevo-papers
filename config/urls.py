from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django_distill import distill_path
from bot.views import home, about, feeds, feed, posts, post
from bot.models import Feed, Post
from bot.feeds import PostsFeed
from bot.sitemaps import sitemaps


# Feed objects function required for static pages
def get_feeds():
    for feed_obj in Feed.objects.order_by("name"):
        yield {"id": feed_obj.id}


# Post objects function required for static pages
def get_posts():
    for post_obj in Post.objects.order_by("-created"):
        yield {"id": post_obj.id}


# Website paths
urlpatterns = [
    distill_path("", home, name="home"),
    distill_path(
        "sitemap.xml",
        sitemap,
        sitemaps,
        name="django.contrib.sitemaps.views.sitemap",
    ),
    distill_path("rss/", PostsFeed(), name="rss"),
    distill_path("about/", about, name="about"),
    distill_path("feeds/", feeds, name="feeds"),
    distill_path("feed/<int:id>/", feed, name="feed", distill_func=get_feeds),
    distill_path("posts/", posts, name="posts"),
    distill_path("post/<int:id>/", post, name="post", distill_func=get_posts),
    path("admin/", admin.site.urls),
]
