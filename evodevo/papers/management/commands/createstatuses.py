from django.core.management.base import BaseCommand
from feeds.models import Post
from papers.models import Status


class Command(BaseCommand):
    help = 'Creates statuses for new posts.'

    def handle(self, *args, **options):

        # Get post IDs for existing statuses
        posts_with_status = Status.objects.values('post_id')

        # Exclude posts that already have a Status instance
        posts_without_status = Post.objects.exclude(id__in=posts_with_status)

        # Exclude posts that are not articles (case insensitive)
        posts_without_status = posts_without_status.exclude(title__istartswith='issue information').exclude(title__istartswith='front cover')

        # Order by oldest to newest using the creation date
        posts_without_status = posts_without_status.order_by('created')

        # Inform how many new posts will be added
        self.stdout.write(f'{posts_without_status.count()} new posts!')

        # Loop over posts and create statuses
        for post in posts_without_status:
            status = Status(post=post)
            status.generate_status_text()
            status.save()

            self.stdout.write(self.style.SUCCESS(f'Status id={status.id}: '),
                              ending='')
            self.stdout.write(f'{status.text}')

