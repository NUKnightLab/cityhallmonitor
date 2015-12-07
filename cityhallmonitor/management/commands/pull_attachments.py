from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
import json
import logging
import requests
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud


logger = logging.getLogger(__name__)

_legistar_matter_attachments_url = \
    'http://webapi.legistar.com/v1/chicago/Matters/%(matter_id)s/Attachments'


class Command(BaseCommand):
    help = 'Get attachments for updated matters from the Chicago Legistar API.'

    _client = None

    def add_arguments(self, parser):
        parser.add_argument('matter_id', nargs='?', help='Matter ID')

    def client(self):
        if self._client is None:
            self._client = DocumentCloud(
                settings.DOCUMENT_CLOUD_USERNAME,
                settings.DOCUMENT_CLOUD_PASSWORD)
        return self._client

    def search(self, query):
        """
        Seach DocumentCloud
        """
        r = self.client().documents.search(query)
        assert type(r) is list, \
            'DocumentCloud search response is %s: %s' % (type(r), repr(r))
        return r
    
    def privatize_doc(self, hyperlink):
        """
        Make doc with source=hyperlink private
        """
        logger.debug('Privatizing %s' % hyperlink)
               
        r = self.search('account:%s project:"%s" access:public source: "%s"' % (
                settings.DOCUMENT_CLOUD_ACCOUNT,
                settings.DOCUMENT_CLOUD_PROJECT, 
                hyperlink))
        if not r:
            logger.info('Skipping privatization (no public version found): %s' \
                % hyperlink)
            return            
        if len(r) > 1:
            raise Exception(
                'Multiple instances exist in DocumentCloud for '\
                'source: %s' % hyperlink)               
        doc = r[0]    
        doc.access = 'private'
        doc.save()
        
    def fetch(self, matter):
        """
        Fetch attachments for matter
        """
        url = _legistar_matter_attachments_url % {'matter_id': matter.id}        
        logger.debug('Downloading %s', url)   
        
        headers = {'Accept': 'text/json'}
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise Exception('Error downloading %s [%d]' \
                % (url, r.status_code))
        for i, item in enumerate(r.json()):
            
            try:
                r = MatterAttachment.objects.get(id=item['MatterAttachmentId'])
                hyperlink = r.hyperlink
            except MatterAttachment.DoesNotExist:
                hyperlink = ''
               
            try:
                r = MatterAttachment.from_json(matter.id, item)

                if hyperlink and r.hyperlink != hyperlink:
                    self.privatize_doc(hyperlink)
               
                r.save()                
            except Exception as e:
                logger.info(item)
                raise e
                
        matter.attachments_obtained_at = timezone.now()
        matter.save()

    def handle(self, *args, **options):
        logger.info('matter_id=%(matter_id)s' % options)
        
        try:
            matter_id = options['matter_id']
            if matter_id:
                logger.info(
                    'Fetching attachments for matter ID %s', matter_id)
                matter = Matter.objects.get(id=matter_id)
                self.fetch(matter)
            else:
                logger.info(
                    'Fetching all updated matter attachments.')
                for matter in Matter.objects.filter(
                        Q(attachments_obtained_at=None)
                        | Q(attachments_obtained_at__lte=F('updated_at'))):
                    self.fetch(matter)
        except Exception as e:
            logger.exception(str(e))
        
        logger.info('Done\n')
                  
