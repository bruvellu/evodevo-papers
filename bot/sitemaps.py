from django.contrib.sitemaps import Sitemap
from bot.models import Feed, Post
from django.urls import reverse


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Post.objects.order_by("-created")

    def lastmod(self, obj):
        return obj.modified


class FeedSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Feed.objects.order_by("name")

    def lastmod(self, obj):
        return obj.modified


class PageSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

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
