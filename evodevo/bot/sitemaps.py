from django.contrib.sitemaps import Sitemap
from bot.models import Feed, Post


class PostSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Post.objects.filter(published=True).order_by("-created_at")

    def lastmod(self, obj):
        return obj.created_at


# Dictionary required for sitemaps
sitemaps = {
    "sitemaps": {
        "posts": PostSitemap,
    }
}





# from django.contrib import sitemaps
# from django.urls import reverse


# class StaticViewSitemap(sitemaps.Sitemap):
    # priority = 0.5
    # changefreq = "daily"

    # def items(self):
        # return ["main", "about", "license"]

    # def location(self, item):
        # return reverse(item)
