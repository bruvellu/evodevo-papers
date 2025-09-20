from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bot.models import Post


class Command(BaseCommand):
    help = "Publish social media statuses for posts."

    def handle(self, *args, **options):
        # Prioritize new posts published in the last 30 days, fallback to older new posts
        one_month_ago = timezone.now() - timedelta(days=30)
        new_post = (
            Post.objects.filter(is_new=True, created__gte=one_month_ago)
            .order_by("?")
            .first()
            or Post.objects.filter(is_new=True).order_by("?").first()
        )

        if new_post:
            self.stdout.write(f"New post found: {new_post}")
            self.publish_post_statuses(new_post)

        else:
            self.stdout.write("No new posts to publish.")

            # Priority 2: Publish a random post with unpublished statuses
            old_post = (
                Post.objects.filter(
                    statuses__is_published=False, statuses__client__is_active=True
                )
                .distinct()
                .order_by("?")
                .first()
            )

            if old_post:
                self.publish_post_statuses(old_post)

            else:
                self.stdout.write("No posts with unpublished statutes.")

                # TODO: Priority 3: Boost a random published post?

    def publish_post_statuses(self, post):
        for status in post.statuses.all():
            self.stdout.write(f"Found status: {status}")
            published = status.publish()
            if published:
                self.stdout.write(
                    f"Published to {status.client.account}: {status.text}"
                )

        post.update_is_new()
