from django.core.management.base import BaseCommand
from bot.models import Post


class Command(BaseCommand):
    help = "Publish social media statuses for posts."

    def handle(self, *args, **options):
        # Priority 1: Publish new posts

        # Fetch oldest unpublished post
        new_post = Post.objects.filter(is_new=True).order_by("created").first()

        if new_post:
            self.stdout.write(f"New post found: {new_post}")
            self.publish_new_post_statuses(new_post)

        else:
            self.stdout.write("No new posts to publish.")

            # TODO: Publish a random post?
            # for client in clients:
            # Client.objects.filter(is_active=True)
            # statuses = Status.objects.filter(client=client)

    def publish_new_post_statuses(self, new_post):
        for status in new_post.statuses.all():
            self.stdout.write(f"Found status: {status}")
            published = status.publish()
            if published:
                self.stdout.write(
                    f"Published to {status.client.account}: {status.text}"
                )

        new_post.update_is_new()
