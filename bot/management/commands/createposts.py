from urllib.parse import urlparse, urlunparse

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.html import strip_tags
from feeds.models import Post as Entry

from bot.models import Post


class Command(BaseCommand):
    help = "Creates posts for new feed entries."

    FILTERED_TITLE_TERMS = ["issue information", "front cover", "erratum"]

    def handle(self, *args, **options):
        """
        Fetches new entries without posts, creates corresponding Post objects,
        and outputs results to the command line.
        """

        new_entries = self.get_new_entries()
        filtered_entries = self.filter_entries(new_entries)

        self.stdout.write(f"{new_entries.count()} total new entries")
        self.stdout.write(
            f"{filtered_entries.count()} remaining new entries (after filtering)"
        )

        for entry in filtered_entries:
            if self.is_duplicate(entry):
                continue
            post = self.create_post_from_entry(entry)
            post.get_or_create_statuses()
            self.stdout.write(f"New post created: {post}")

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
            entry=entry,
            title=self.clean_title(entry.title),
            link=entry.link,
            feed=entry.source.feed,
            created=entry.created,
        )
        post.save()
        return post

    def clean_title(self, title):
        """Remove HTML tags from title."""
        return strip_tags(title)

    def is_duplicate(self, entry):
        """Check if a post already exists for an entry."""
        # TODO: Create test for duplicate detection
        posts_with_identical_title = Post.objects.filter(title=entry.title)
        for post in posts_with_identical_title:
            self.stdout.write(f"\n{entry.title}")
            self.stdout.write(
                f"Sources: entry='{entry.source}', post='{post.entry.source}'"
            )
            if not entry.source == post.entry.source:
                self.stdout.write(
                    self.style.WARNING(
                        f"Different sources. Potential duplicate! Skipping..."
                    )
                )
                return True
            self.stdout.write(
                self.style.WARNING(f"Same title and source. Likely not a duplicate...")
            )
        return False
