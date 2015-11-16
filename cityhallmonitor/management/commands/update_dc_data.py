import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update Matter-related document data in DocumentCloud'
    
    _client = None

    def client(self):
        if self._client is None:
            self._client = DocumentCloud(
                settings.DOCUMENT_CLOUD_USERNAME,
                settings.DOCUMENT_CLOUD_PASSWORD)
        return self._client

    def add_arguments(self, parser):
        parser.add_argument('query', help='DocumentCloud search query')

    def get_project(self, name):
        return self.client().projects.get_by_title(name)

    def search(self, query):
        """Seach DocumentCloud"""
        return self.client().documents.search(query)
 
    def datadiff(self, d1, d2):
        return set(
            [ (k,v) for k,v in d1.items() ]).symmetric_difference(
            set([ (k,v) for k,v in d2.items() ]))

    def check_update(self, doc):
        """Update document data in DocumentCloud"""
        attachment_id = doc.data['MatterAttachmentId']
        attachment = MatterAttachment.objects.get(id=attachment_id)
           
        matter = attachment.matter
        sort_date = max([d for d in [
                matter.intro_date, 
                matter.agenda_date, 
                matter.passed_date, 
                matter.enactment_date] if d is not None], default=None)
        data = {
            'MatterAttachmentId': str(attachment.id),
            'MatterId': str(matter.id),
            'MatterFile': matter.file,
            'MatterName': matter.name,
            'MatterTitle': matter.title,
            'MatterType': matter.matter_type.name,
            'MatterStatus': matter.matter_status.name,
            'MatterIntroDate': str(matter.intro_date),
            'MatterAgendaDate': str(matter.agenda_date),
            'MatterPassedDate': str(matter.passed_date),
            'MatterEnactmentDate': str(matter.enactment_date),
            'MatterEnactmentNumber': str(matter.enactment_number),
            'MatterRequester': matter.requester,
            'MatterNotes': matter.notes,
            'MatterSortDate': str(sort_date),
            'MatterSortMonth': sort_date.strftime('%Y-%m'),
            'MatterSortYear': sort_date.strftime('%Y')
        }
           
        olddata = { k:v for k,v in doc.data.items()
            if k != 'ops:DescriptionProcessed' }
        if self.datadiff(data, olddata):
            logger.debug('Updating metadata for document: %s', 
                attachment.hyperlink)
                        
            if not doc.data:
                data['ops:DescriptionProcessed'] = '0'
            doc.data = data
            doc.put()
       
    def handle(self, *args, **options):
        logger.info('query="%(query)s"', options)
                    
        try:
            logger.info('Searching DocumentCloud')
            r = self.search('account:%s project:"%s" %s' % (
                    settings.DOCUMENT_CLOUD_ACCOUNT,
                    settings.DOCUMENT_CLOUD_PROJECT, 
                    options['query']))
            
            logger.info('Found %d matching documents' % len(r))
            
            for doc in r:
                try:
                    self.check_update(doc)  
                except Exception as ex:
                    logger.error(doc.data)
                    logger.exception(str(ex))            
        except Exception as e:
            logger.exception(str(e))
              
        logger.info('Done\n')
        
