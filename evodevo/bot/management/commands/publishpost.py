from django.core.management.base import BaseCommand
from bot.models import Client, Post
from mastodon import Mastodon


class Command(BaseCommand):
    help = 'Publish single post to Mastodon.'

    def handle(self, *args, **options):

        # Get the oldest unpublished post object
        post = Post.objects.filter(published=False).order_by('id').first()

        if post:
            client = Client.objects.get(account='@evodevo_papers@biologists.social')
            mastodon = Mastodon(access_token=client.access_token,
                                api_base_url=client.api_base_url)
            response = mastodon.status_post(post.text,
                                            visibility='unlisted',
                                            language='en')

            post.created_at = response['created_at']
            post.publication_id = str(response['id'])
            post.url = response['url']
            post.response = response
            post.published = True
            post.save()

            self.stdout.write(f'{post.text}')
            self.stdout.write(f'{post.url}')

