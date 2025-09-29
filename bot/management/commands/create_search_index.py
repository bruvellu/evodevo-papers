import os
import json

from django.core.management import call_command
from django.core.management.base import BaseCommand

from bot.models import Post


class Command(BaseCommand):
    help = "Create search index for post objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="static/",
            help="Directory to save the search index (default: static/)",
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]

        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Fetch all posts
        self.stdout.write("Fetching posts...")
        posts = Post.objects.values("id", "title")
        search_index = "search_index.json"

        # Write to a JSON file directly
        self.stdout.write("Writing index...")
        with open(f'{output_dir}/{search_index}', 'w') as json_file:
            json.dump(list(posts), json_file, indent=4) 

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {search_index} in {output_dir}")
        )
