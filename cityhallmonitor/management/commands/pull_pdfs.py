import urllib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud

API_DATA_TYPE = 'MatterAttachments'
USERNAME = settings.DOCUMENT_CLOUD_USERNAME
PASSWORD = settings.DOCUMENT_CLOUD_PASSWORD
DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT

class Command(BaseCommand):
    help = 'Get PDF links for new/updated attachments from the chicago legistar API.'

    def add_arguments(self, parser):
        parser.add_argument('matter_id', nargs='?', help='Matter ID')
        parser.add_argument('--all', action='store_true',
            help='Process all attachments.')

    def upload_to_doccloud(self, url, title):
        client = DocumentCloud(USERNAME, PASSWORD)
        new_document = client.documents.upload(
            url, title, access='public', source=url
            # TODO: put some useful metadata here.
            #data = { 'fake_data': 'something arbitrary' }
        )
        self.stdout.write(new_document.get_pdf_url())

    def search(self, query):
        return DocumentCloud(USERNAME, PASSWORD).documents.search(query)

    def fetch(self, attachment):
        r = self.search('account:%s source: "%s"' % (
            DOCUMENT_CLOUD_ACCOUNT, attachment.hyperlink))
        if r:
            self.stdout.write(
                'Document exists in DocumentCloud. Not transferring: %s' % (
                attachment.hyperlink))
            if len(r) > 1:
                self.stdout.write(
                    'WARNING: multiple instances exist in DocumentCloud for '\
                    'document: %s' % attachment.hyperlink)
        else:
            self.stdout.write(
                'Transferring to Document Cloud: %s...' % attachment.hyperlink)   
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
            q = MatterAttachment.objects.all()
            if options['all']:
                self.stdout.write('Fetching all matter attachment links.')
            else:
                self.stdout.write('Fetching all new matter attachment links.')
                q = q.filter(
                    Q(link_obtained_at=None)
                    | Q(link_obtained_at__lte=F('last_modified')) )
            for attachment in q:
                self.fetch(attachment)
                attachment.link_obtained_at = timezone.now()
                attachment.save()
        self.stdout.write('Done')
        
