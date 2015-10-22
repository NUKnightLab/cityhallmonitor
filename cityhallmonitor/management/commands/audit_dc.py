from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging
import pprint
from cityhallmonitor.models import Matter, MatterAttachment, MatterType
from documentcloud import DocumentCloud
from smtplib import SMTPException


logger = logging.getLogger(__name__)


DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT

DEFAULT_PROJECT = 'Chicago City Hall Monitor'


class Command(BaseCommand):
    help = 'Compare public data in DocumentCloud vs DB.'
    
    _client = None

    def client(self):
        """Using un-authenticated client..."""
        if self._client is None:
            self._client = DocumentCloud()
        return self._client

    def add_arguments(self, parser):
        parser.add_argument('query', nargs='?', help='DocumentCloud search query')

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
 
 
    def process_document(self, doc):
        """
        Compare data when searching by source and by id
        """ 
        # Query database by source      
        qs = MatterAttachment.objects.filter(hyperlink=doc.source)
        n = len(qs)
        if not n:
            logger.error(
                'source not found in db [source=%s]' % (
                doc.source)
            )   
        elif n > 1:
            logger.error(
                'source matches multiple in db [source=%s]' % (
                doc.source)
            )  
        else:
            attachment = qs[0]
            delta = self.diff_data(attachment, doc)                  
            if delta:
                logger.error('Data mismatch by source [source=%s]\n%s' % (
                    attachment.hyperlink, pprint.pformat(delta, width=100))
                ) 
        
        # Query database by MatterAttachmentId
        qs = MatterAttachment.objects.filter(id=doc.data['MatterAttachmentId'])
        n = len(qs)
        if not n:
            logger.error(
                'MatterAttachmentId not found in db [id=%s]' % (
                doc.data['MatterAttachmentId'])
            )   
        else:
            attachment = qs[0]
            delta = self.diff_data(attachment, doc)                  
            if delta:
                logger.error('Data mismatch by MatterAttachmentId [MatterAttachmentId=%s]\n%s' % (
                    doc.data['MatterAttachmentId'], pprint.pformat(delta, width=100))
                ) 
        

    def handle(self, *args, **options):
        try:
            query = options['query']
            if query:
                logger.info('Searching DocumentCloud [%s]' % query)
                r = self.search('account:%s project:"%s" access:public %s' % (
                    DOCUMENT_CLOUD_ACCOUNT, DEFAULT_PROJECT, query))
            else:
                logger.info('Searching DocumentCloud')
                r = self.search('account:%s project:"%s" access:public' % (
                    DOCUMENT_CLOUD_ACCOUNT, DEFAULT_PROJECT))
                        
            logger.info('Found %d matching documents' % len(r))
                                
            for (i, doc) in enumerate(r, start=1):
                self.process_document(doc)  
                if i and (i % 1000) == 0:
                    logger.debug('Processed %d documents' % i)

        except Exception as e:
            logger.exception(str(e))
              
        logger.info('Done\n')

        
