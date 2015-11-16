from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging
import pprint
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud
from smtplib import SMTPException


logger = logging.getLogger(__name__)


ATTACHMENT_PUBLISH_URL = 'https://cityhallmonitor.knightlab.com/documents/%d'


class Command(BaseCommand):
    help = 'Compare data in DB vs DocumentCloud.'
    
    _client = None

    def client(self):
        """Using un-authenticated client..."""
        if self._client is None:
            self._client = DocumentCloud()
        return self._client

    def add_arguments(self, parser):
        parser.add_argument('id', nargs='?', help='start with id')

    def search(self, query):
        """Search document cloud and verify response type"""
        r = self.client().documents.search(query)
        assert type(r) is list, \
            'DocumentCloud search response is %s: %s' % (type(r), repr(r))
        return r

    def datadiff(self, d1, d2):
        """
        Return differences between two dictionaries
        **Only looks at keys in d1, in case of field additions.**
        """
        ks = d1.keys()
        return set(
            [ (k, d1.get(k)) for k in ks ]).symmetric_difference(
            set([ (k, d2.get(k)) for k in ks ]))       
        #return set(
        #    [ (k,v) for k,v in d1.items() ]).symmetric_difference(
        #    set([ (k,v) for k,v in d2.items() ]))

    def compose_data(self, attachment):
        """
        Return document data for attachment
        """
        matter = attachment.matter
        published_url = ATTACHMENT_PUBLISH_URL % attachment.id
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
            'MatterSortDate': str(sort_date)
        }   
        return data     
    
    
    def diff_data(self, attachment, doc):
        """
        Diff data in attachment vs documentcloud record
        """       
        data = self.compose_data(attachment)
        dc_data = {k:v for k,v in doc.data.items() if k != 'ops:DescriptionProcessed'}     
        return self.datadiff(data, dc_data)      
 
 
    def process_attachment(self, attachment):
        """
        Compare data when searching by source and by id
        """
        # Search by source
        r = self.search('account:%s project:"%s" source: "%s"' % (
                settings.DOCUMENT_CLOUD_ACCOUNT, 
                settings.DOCUMENT_CLOUD_PROJECT,
                attachment.hyperlink))       
        if not r:
            logger.error(
                'source not found in DC [id=%d, source=%s]' % (
                attachment.id, attachment.hyperlink)
            )   
        elif len(r) > 1:
            logger.error(
                'source matches multiple in DC [id=%d, source=%s]' % (
                attachment.id, attachment.hyperlink)
            )                
        else:
            delta = self.diff_data(attachment, r[0])    
            if delta:
                logger.error('Data mismatch by source [id=%d, source=%s]\n%s' % (
                    attachment.id, attachment.hyperlink, pprint.pformat(delta, width=100))
                )                      
           
        # Search DC by MatterAttachmentId
        r = self.search('account:%s project:"%s" MatterAttachmentId:%d' % (
                settings.DOCUMENT_CLOUD_ACCOUNT, 
                settings.DOCUMENT_CLOUD_PROJECT,
                attachment.id))   
        if not r:
            logger.error(
                'MatterAttachmentId not found in DC [id=%d, source=%s]' % (
                attachment.id, attachment.hyperlink)
            )   
        elif len(r) > 1:
            logger.error(
                'MatterAttachmentId matches multiple in DC [id=%d, source=%s]' % (
                attachment.id, attachment.hyperlink)
            )                
        else:
            delta = self.diff_data(attachment, r[0])    
            if delta:
                logger.error('Data mismatch by MatterAttachmentId [id=%d, source=%s]\n%s' % (
                    attachment.id, attachment.hyperlink, pprint.pformat(delta, width=100))
                )                      
        
                                                               
    def handle(self, *args, **options):
        logger.info('id=%(id)s' % options)
        
        try:
            id = options['id']
            if id:
                logger.info('Auditing attachments with id >= %s', id)
                qs = MatterAttachment.objects.filter(id__gte=id).order_by('id')
            else:
                logger.info('Auditing all attachments')
                qs = MatterAttachment.objects.all().order_by('id')
   
            logger.info('Processing %d attachments', len(qs))
       
            for (i, r) in enumerate(qs, start=1):
                self.process_attachment(r)
                if i and (i % 1000) == 0:
                    logger.debug('Processed %d attachments' % i)
                               
        except Exception as e:
            logger.exception(str(e))
                   
        logger.info('Done')
        
