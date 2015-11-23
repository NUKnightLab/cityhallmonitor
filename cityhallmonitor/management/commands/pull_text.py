import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cityhallmonitor.models import MatterAttachment
from documentcloud import DocumentCloud


logger = logging.getLogger(__name__)

DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT
DOCUMENT_CLOUD_PROJECT = settings.DOCUMENT_CLOUD_PROJECT


class DocumentSyncException(Exception): pass


class Command(BaseCommand):
    help = 'Pull extracted text and id from DocumentCloud'

    _client = None

    def client(self):
        if self._client is None:
            self._client = DocumentCloud(
                settings.DOCUMENT_CLOUD_USERNAME,
                settings.DOCUMENT_CLOUD_PASSWORD)
        return self._client

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='Process up to LIMIT documents')

    def get_project(self, name):
        return self.client().projects.get_by_title(name)

    def search(self, query):
        """Seach DocumentCloud"""
        r = self.client().documents.search(query)
        assert type(r) is list, \
            'DocumentCloud search response is %s: %s' % (type(r), repr(r))
        return r

    def fetch(self, attachment):
        """Get extracted text and id from DocumentCloud"""
        r = self.search('account:%s project:"%s" source: "%s" access:public' % (
                DOCUMENT_CLOUD_ACCOUNT, 
                DOCUMENT_CLOUD_PROJECT, 
                attachment.hyperlink))

        if r:
            if len(r) > 1:
                raise DocumentSyncException(
                    'Multiple instances exist in DocumentCloud for '\
                    'document: %s' % attachment.hyperlink)
            logger.info('Processing: %s' % attachment.hyperlink)
            
            doc = r[0]
            
            attachment.dc_id = doc.id
            attachment.text = doc.full_text or ''
            attachment.save()            
        else:
            logger.error('Document not found: %s' % attachment.hyperlink)
           
    def handle(self, *args, **options):
        logger.info('limit=%(limit)s', options)
        try:
            qs = MatterAttachment.objects.filter(text='')
            
            if options['limit']:
                for attachment in qs[:options['limit']]:
                    self.fetch(attachment)
            else:
                for attachment in qs:
                    self.fetch(attachment)
                
        except Exception as e:
            logger.exception(str(e))

        logger.info('Done\n')

