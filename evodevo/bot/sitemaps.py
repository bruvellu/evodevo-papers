from django.contrib.sitemaps import Sitemap
from bot.models import Feed, Post
from django.urls import reverse


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(published=True).order_by("-created_at")

    def lastmod(self, obj):
        return obj.created_at


class FeedSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Feed.objects.order_by("name")

    # def lastmod(self, obj):
        # return obj.created_at


class PageSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["rss", "about", "feeds", "posts"]

    def location(self, item):
        return reverse(item)


# Dictionary required for sitemaps
sitemaps = {
    "sitemaps": {
        "posts": PostSitemap,
        "feeds": FeedSitemap,
        "pages": PageSitemap,
    }
}




