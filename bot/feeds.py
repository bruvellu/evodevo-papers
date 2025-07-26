from django.contrib.syndication.views import Feed

from bot.models import Post


class PostsFeed(Feed):
    title = "EvoDevo Papers latest posts"
    link = "/feed/"
    description = "Posting the latest papers in evolutionary developmental biology."

    def items(self):
        return Post.objects.order_by("-created")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.display_text
