from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud

API_DATA_TYPE = 'MatterAttachments'
USERNAME = settings.DOCUMENT_CLOUD_USERNAME
PASSWORD = settings.DOCUMENT_CLOUD_PASSWORD


class Command(BaseCommand):
    help = 'Get PDF links for new/updated attachments from the chicago legistar API.'

    def add_arguments(self, parser):
        parser.add_argument('matter_id', nargs='?', help='Matter ID')

    def upload_to_doccloud(self, url, title):
        client = DocumentCloud(USERNAME, PASSWORD)
        # Note: this code depends on python-documentcloud implementation
        # of URL based uploads -- functionality still pending.
        new_document = client.documents.upload(
            url, title, access='public', source=url
            # TODO: put some useful metadata here.
            #data = { 'fake_data': 'something arbitrary' }
        )
        self.stdout.write(new_document.get_pdf_url())

    def fetch(self, attachment):
        self.stdout.write(
            'Transfering to Document Cloud: %s...' % attachment.hyperlink)   
        # TODO: We should check to see if the document exists in
        #       document cloud before uploading
        self.upload_to_doccloud(attachment.hyperlink, attachment.name)

    def handle(self, *args, **options):
        matter_id = options['matter_id']
        if matter_id:
            self.stdout.write(
                'Fetching attachment links for matter ID %s.' % matter_id)
            for attachment in MatterAttachment.objects.filter(
                    matter_id=matter_id):
                self.fetch(attchment)
        else:
            self.stdout.write('Fetching all new matter attachment links.')
            for attachment in MatterAttachment.objects.filter(
                    Q(link_obtained_at=None)
                    | Q(link_obtained_at__lte=F('last_modified')) ):
                self.fetch(attachment)
                attachment.link_obtained_at = timezone.now()
                attachment.save()
        self.stdout.write('Done')
        
