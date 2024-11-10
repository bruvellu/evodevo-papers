from django.core.management.base import BaseCommand
from feeds.models import Post as Entry
from bot.models import Post


class Command(BaseCommand):
    help = 'Creates statuses for new feed entries.'

    def handle(self, *args, **options):

        # Get entry IDs for existing statuses
        entries_with_status = Post.objects.values('entry_id')

        # Exclude entries that already have a Post instance
        entries_without_status = Entry.objects.exclude(id__in=entries_with_status)

        # Exclude entries that are not articles (case insensitive)
        entries_without_status = entries_without_status.exclude(title__istartswith='issue information').exclude(title__istartswith='front cover')

        # Order by oldest to newest using the creation date
        entries_without_status = entries_without_status.order_by('created')

        # Inform how many new entries will be added
        self.stdout.write(f'{entries_without_status.count()} new feed entries!')

        # Loop over new feed entries and create statuses
        for entry in entries_without_status:
            status = Post(entry=entry)
            status.generate_text()
            status.save()

            self.stdout.write(self.style.SUCCESS(f'Post id={status.id}: '),
                              ending='')
            self.stdout.write(f'{status.text}')

