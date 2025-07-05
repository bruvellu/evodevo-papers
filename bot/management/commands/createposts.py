from django.core.management.base import BaseCommand
from feeds.models import Post as Entry
from bot.models import Post


class Command(BaseCommand):
    help = "Creates posts for new feed entries."

    def handle(self, *args, **options):
        # Get entry IDs for existing posts
        entries_with_a_post = Post.objects.values("entry_id")

        # Exclude entries that already have a Post instance
        entries_without_a_post = Entry.objects.exclude(id__in=entries_with_a_post)

        # Exclude entries that are not articles (case insensitive)
        entries_without_a_post = entries_without_a_post.exclude(
            title__istartswith="issue information"
        ).exclude(title__istartswith="front cover")

        # Order by oldest to newest using the creation date
        entries_without_a_post = entries_without_a_post.order_by("created")

        # Inform how many new entries will be added
        self.stdout.write(f"{entries_without_a_post.count()} new feed entries!")

        # Loop over new feed entries and create posts and statuses
        for entry in entries_without_a_post:
            # New post
            post = Post(entry=entry)
            post.save()
            # Associated statuses
            post.create_statuses()
            # Write output
            self.stdout.write(self.style.SUCCESS(f"Post id={post.id}: "), ending="")
            self.stdout.write(f"{post.text}")
