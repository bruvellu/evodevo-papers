import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from bot.models import Post


class Command(BaseCommand):
    help = "Create test fixtures from 10 random posts and their related objects"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="bot/fixtures",
            help="Directory to save fixture files (default: bot/fixtures)",
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]

        # Ensure fixtures directory exists
        os.makedirs(output_dir, exist_ok=True)

        # 1. Fetch 10 random posts
        self.stdout.write("Fetching 10 random posts...")
        random_posts = (
            Post.objects.select_related("entry__source__feed")
            .prefetch_related("statuses")
            .order_by("?")[:10]
        )

        if not random_posts.exists():
            self.stdout.write(self.style.WARNING("No posts found in database!"))
            return

        # 2. Collect all related object PKs
        post_pks = []
        entry_pks = []
        source_pks = []
        feed_pks = []
        status_pks = []
        client_pks = []

        for post in random_posts:
            post_pks.append(post.pk)
            entry_pks.append(post.entry.pk)
            source_pks.append(post.entry.source.pk)
            feed_pks.append(post.entry.source.feed.pk)
            for status in post.statuses.all():
                status_pks.append(status.pk)
                client_pks.append(status.client.pk)

        # 3. Export posts to fixtures
        self.dumpdata(name="posts", model="bot.Post", pks=post_pks, outdir=output_dir)
        self.dumpdata(
            name="entries", model="feeds.Post", pks=entry_pks, outdir=output_dir
        )
        self.dumpdata(
            name="sources", model="feeds.Source", pks=source_pks, outdir=output_dir
        )
        self.dumpdata(name="feeds", model="bot.Feed", pks=feed_pks, outdir=output_dir)
        self.dumpdata(
            name="statuses", model="bot.Status", pks=status_pks, outdir=output_dir
        )
        self.dumpdata(
            name="clients", model="bot.Client", pks=client_pks, outdir=output_dir
        )

        # if post_pks:
        # self.stdout.write("Exporting posts")
        # post_pks_str = ",".join(str(pk) for pk in post_pks)
        # call_command(
        # "dumpdata",
        # "bot.Post",
        # pks=post_pks_str,
        # indent=2,
        # output=f"{output_dir}/posts.json",
        # )

        # 4. Export entries to fixtures
        # if entry_pks:
        # self.stdout.write("Exporting entries")
        # entry_pks_str = ",".join(str(pk) for pk in entry_pks)
        # call_command(
        # "dumpdata",
        # "feeds.Post",
        # pks=entry_pks_str,
        # indent=2,
        # output=f"{output_dir}/entries.json",
        # )

        # 5. Export sources to fixtures
        # if source_pks:
        # self.stdout.write("Exporting sources")
        # source_pks_str = ",".join(str(pk) for pk in source_pks)
        # call_command(
        # "dumpdata",
        # "feeds.Source",
        # pks=source_pks_str,
        # indent=2,
        # output=f"{output_dir}/sources.json",
        # )

        # 6. Export feeds to fixtures
        # if feed_pks:
        # self.stdout.write("Exporting feeds")
        # feed_pks_str = ",".join(str(pk) for pk in feed_pks)
        # call_command(
        # "dumpdata",
        # "bot.Feed",
        # pks=feed_pks_str,
        # indent=2,
        # output=f"{output_dir}/feeds.json",
        # )

        # 7. Export statuses to fixtures
        # if status_pks:
        # self.stdout.write("Exporting statuses")
        # status_pks_str = ",".join(str(pk) for pk in status_pks)
        # call_command(
        # "dumpdata",
        # "bot.Status",
        # pks=status_pks_str,
        # indent=2,
        # output=f"{output_dir}/statuses.json",
        # )

        # 8. Export clients to fixtures
        # if client_pks:
        # self.stdout.write("Exporting clients")
        # client_pks_str = ",".join(str(pk) for pk in client_pks)
        # call_command(
        # "dumpdata",
        # "bot.Client",
        # pks=client_pks_str,
        # indent=2,
        # output=f"{output_dir}/clients.json",
        # )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created fixtures in {output_dir}/")
        )
        self.stdout.write(f"- posts.json ({len(post_pks)} objects)")
        self.stdout.write(f"- entries.json ({len(entry_pks)} objects)")
        self.stdout.write(f"- sources.json ({len(source_pks)} objects)")
        self.stdout.write(f"- feeds.json ({len(feed_pks)} objects)")
        self.stdout.write(f"- statuses.json ({len(status_pks)} objects)")
        self.stdout.write(f"- clients.json ({len(client_pks)} objects)")

    def clean_pks(self, pks):
        # Remove duplicates and convert to strings
        return list(set(pks))

    def dumpdata(self, name, model, pks, outdir):
        if pks:
            pks_str = ",".join(str(pk) for pk in self.clean_pks(pks))
            call_command(
                "dumpdata",
                model,
                pks=pks_str,
                indent=2,
                output=f"{outdir}/{name}.json",
                verbosity=0
            )
