from django.core.management.base import BaseCommand
from bot.models import Client, Post, Status


class Command(BaseCommand):
    help = "Publish statuses for a single new post."

    def handle(self, *args, **options):

        # Fetch the oldest unpublished post
        new_post = Post.objects.filter(is_new=True).order_by('created').first()

        # Publish new post statuses (for each active client)
        if new_post:
            for status in new_post.statuses.all():
                response = status.publish()
                if response:
                    self.stdout.write(f"Posted to {status.client.account}: {status.text}")
            new_post.update_is_new()
        else:
            self.stdout.write("No new posts to publish!")

            # TODO: Publish a random post?
            # for client in clients:
            # Client.objects.filter(is_active=True)
                # statuses = Status.objects.filter(client=client)

