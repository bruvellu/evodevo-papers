from django.contrib.syndication.views import Feed
from django.urls import reverse
from bot.models import Post

class PostsFeed(Feed):
    title = "EvoDevo Papers latest posts"
    link = "/feed/"
    description = "Posting the latest papers in evolutionary developmental biology."

    def items(self):
        return Post.objects.filter(published=True).order_by("-created")[:20]

    def item_title(self, item):
        return item.entry.title

    def item_description(self, item):
        return item.text
