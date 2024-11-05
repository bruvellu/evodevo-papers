from django.core.management.base import BaseCommand
from papers.models import Status
from clients.models import Client
from mastodon import Mastodon


class Command(BaseCommand):
    help = 'Publish single status to Mastodon.'

    def handle(self, *args, **options):

        # Get the oldest unpublished status object
        status = Status.objects.filter(published=False).order_by('id').first()

        # TODO: Pass client account as an argument

        if status:
            client = Client.objects.get(account='@evodevo_papers@biologists.social')
            mastodon = Mastodon(access_token=client.access_token,
                                api_base_url=client.api_base_url)
            response = mastodon.status_post(status.text,
                                            visibility='unlisted',
                                            language='en')

            status.created_at = response['created_at']
            status.publication_id = str(response['id'])
            status.url = response['url']
            status.response = response
            status.published = True
            status.save()

            self.stdout.write(f'{status.text}')
            self.stdout.write(f'{status.url}')

