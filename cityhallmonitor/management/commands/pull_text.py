import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cityhallmonitor.models import MatterAttachment, Document
from documentcloud import DocumentCloud


logger = logging.getLogger(__name__)

DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT
DOCUMENT_CLOUD_PROJECT = settings.DOCUMENT_CLOUD_PROJECT


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
 
    def search(self, query):
        """Seach DocumentCloud"""
        r = self.client().documents.search(query)
        assert type(r) is list, \
            'DocumentCloud search response is %s: %s' % (type(r), repr(r))
        return r

    def fetch(self, attachment):
        """Get extracted text and id from DocumentCloud"""
        try:
            r = self.search('account:%s project:"%s" source: "%s" access:public' % (
                    DOCUMENT_CLOUD_ACCOUNT, 
                    DOCUMENT_CLOUD_PROJECT, 
                    attachment.hyperlink))
            
            if not r:
                raise Exception('not found')
            if len(r) > 1:
                raise Exception('multiple instances')
                
            logger.debug('Processing: %s' % attachment.hyperlink)
        
            doc = r[0]
            if doc.full_text:      
                attachment.dc_id = doc.id
                attachment.save()            
                Document.create_from_attachment(attachment, doc.full_text) 
        except Exception as e:
            logger.error('Error processing %s [%s]' \
                % (attachment.hyperlink, str(e)))
           
    def handle(self, *args, **options):
        logger.info('limit=%(limit)s', options)
 
        try:
            qs = MatterAttachment.objects.filter(document=None)
           
            if options['limit']:
                for attachment in qs[:options['limit']]:
                    self.fetch(attachment)    
            else:
                for attachment in qs:
                    self.fetch(attachment)                     
                 
        except Exception as e:
            logger.exception(str(e))

        logger.info('Done\n')

