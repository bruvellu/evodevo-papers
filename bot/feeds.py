from django.contrib.syndication.views import Feed
from django.template.loader import render_to_string

from bot.models import Post


class PostsFeed(Feed):
    title = "EvoDevo Papers latest posts"
    link = "/feed/"
    description = "Streaming the latest papers in evolutionary developmental biology."

    def items(self):
        return Post.objects.order_by("-created")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return render_to_string("rss_item_description.html", {"item": item})
