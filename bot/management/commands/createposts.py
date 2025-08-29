from django.core.management.base import BaseCommand
from django.db.models import Q
from feeds.models import Post as Entry
from urllib.parse import urlparse, urlunparse


from bot.models import Post


class Command(BaseCommand):
    help = "Creates posts for new feed entries."

    FILTERED_TITLE_TERMS = ["issue information", "front cover"]

    def handle(self, *args, **options):
        """
        Fetches new entries without posts, creates corresponding Post objects,
        and outputs results to the command line.
        """

        new_entries = self.get_new_entries()
        filtered_entries = self.filter_entries(new_entries)

        self.stdout.write(f"{new_entries.count()} total new entries")
        self.stdout.write(f"{filtered_entries.count()} filtered new entries")

        for entry in filtered_entries:
            post = self.create_post_from_entry(entry)
            post.get_or_create_statuses()
            self.stdout.write(self.style.SUCCESS(str(post)))

    def get_new_entries(self):
        """
        Returns a queryset of Entry objects that do not have
        an associated Post. Ignore entries with specific terms.
        Order entries by creation date (oldest first).
        """
        # Get the entry IDs of existing posts
        entries_with_posts = Post.objects.values_list("entry_id", flat=True)

        # Exclude entries that already have a Post instance
        entries_without_a_post = Entry.objects.exclude(id__in=entries_with_posts)

        # Order by oldest to newest using the creation date
        entries_without_a_post = entries_without_a_post.order_by("created")

        return entries_without_a_post

    def filter_entries(self, entries):
        """
        Exclude entries whose title contains any of the filtered terms (case-insensitive).
        """
        q = Q()
        for term in self.FILTERED_TITLE_TERMS:
            q |= Q(title__icontains=term)
        return entries.exclude(q)

    def create_post_from_entry(self, entry):
        """
        Creates and saves a new Post object from a given Entry instance.
        Returns the created Post object.
        """
        post = Post(
            entry=entry, title=entry.title, link=self.clean_url(entry.link), created=entry.created
        )
        post.save()
        return post

    def clean_url(self, url):
        """Remove query parameters and fragments from a URL, robustly."""
        # Create tests for URL parsing errors
        parsed = urlparse(url)
        clean_parsed = parsed._replace(params='', query='', fragment='')
        return urlunparse(clean_parsed)
