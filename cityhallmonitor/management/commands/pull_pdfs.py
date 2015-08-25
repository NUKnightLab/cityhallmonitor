import logging
import re
import urllib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud


logger = logging.getLogger(__name__)

USERNAME = settings.DOCUMENT_CLOUD_USERNAME
PASSWORD = settings.DOCUMENT_CLOUD_PASSWORD
DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT
ATTACHMENT_PUBLISH_URL = 'https://cityhallmonitor.knightlab.com/documents/%d'
DEFAULT_PROJECT = 'Chicago City Hall Monitor'
DOCCLOUD_RESERVED_KEYS = set([
    'person',
    'organization',
    'place',
    'term',
    'email',
    'phone',
    'city',
    'state',
    'country',
    'title',
    'description',
    'source',
    'account',
    'group',
    'project',
    'projectid',
    'document',
    'access',
    'filter'])

"""
Document types from the document names seem to be a bit unreliable. Thus,
we are currently not using these, but the tentative mapping is here for
reference.
"""
DOCUMENT_TYPES = (
    ('SA', 'Substitute Appointment'),
    ('SO', 'Substitute Ordinance'),
    ('SR', 'Substitute Resolution'),
    ('SOr', 'Substitute Order'),
    ('Or', 'Order'),
    ('F', 'Filing'), # ?? seems to be used for 'Communication' matter type
    ('O', 'Ordinance'),
    ('R', 'Resolution'),
    ('CL', 'Claim'),
    ('F', 'Filed Matter'),
    ('A', 'Appointment'),
)
DOCUMENT_TYPE_MATCHER = re.compile('^(%s)\d+-\d+(\.(pdf|rtf))?$' % '|'.join(
    [code for code,name in DOCUMENT_TYPES]))

class DocumentSyncException(Exception): pass

class Command(BaseCommand):
    help = 'Upload updated attachment files from the Chicago Legistar API to DocumentCloud'
    
    _client = None

    def client(self):
        if self._client is None:
            self._client = DocumentCloud(USERNAME, PASSWORD)
        return self._client

    def add_arguments(self, parser):
        parser.add_argument('matter_id', nargs='?', help='Matter ID')
        parser.add_argument('--all', action='store_true',
            help='Process all attachments.')
        parser.add_argument('--deleteall', action='store_true',
            help='WARNING: Deletes all documents in DocumentCloud. '\
            'Other flags are ignored and no new documents processed.')

    def get_project(self, name):
        return self.client().projects.get_by_title(name)

    def upload_to_doccloud(self, url, title, data=None,
            project_id=None, published_url=None):
        """Upload a document to DocumentCloud"""
        if data is not None:
            assert not(set(data).intersection(DOCCLOUD_RESERVED_KEYS))
        new_document = self.client().documents.upload(
            url, title, access='public', source=url, data=data,
            project=project_id, published_url=published_url
        )
        logger.debug(new_document.get_pdf_url())
        return new_document

    def search(self, query):
        """Seach DocumentCloud"""
        return self.client().documents.search(query)
 
    def short_description(self, attachment):
        """Get short description for attachment"""
        filename = '.'.join(attachment.name.split('.')[:-1])
        return '%s %s' % (attachment.matter.matter_type.name, filename)

    def datadiff(self, d1, d2):
        return set(
            [ (k,v) for k,v in d1.items() ]).symmetric_difference(
            set([ (k,v) for k,v in d2.items() ]))

    def fetch(self, attachment, project_id):
        """Upload attachment file to DocumentCloud"""
        matter = attachment.matter
        published_url = ATTACHMENT_PUBLISH_URL % attachment.id
        description = self.short_description(attachment)
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
            'MatterNotes': matter.notes
        }
        r = self.search('account:%s source: "%s"' % (
            DOCUMENT_CLOUD_ACCOUNT, attachment.hyperlink))
      
        assert type(r) is list, \
            'DocumentCloud search response is %s: %s' % (type(r), repr(r))
           
        if r:
            logger.debug(
                'Document exists in DocumentCloud. Not transferring: %s',                
                attachment.hyperlink)
                
            if len(r) > 1:
                raise DocumentSyncException(
                    'Multiple instances exist in DocumentCloud for '\
                    'document: %s' % attachment.hyperlink)
            else:
                doc = r[0]
                olddata = { k:v for k,v in doc.data.items()
                    if k != 'ops:DescriptionProcessed' }
                if self.datadiff(data, olddata):
                    logger.debug('Updating metadata for document: %s', 
                        attachment.hyperlink)
                    if not doc.data:
                        data['ops:DescriptionProcessed'] = '0'
                    doc.data = data
                    doc.put()
        else:
            logger.info('Transferring to DocumentCloud: %s', 
                attachment.hyperlink)   
            data['ops:DescriptionProcessed'] = '0'
            doc = self.upload_to_doccloud(
                attachment.hyperlink, attachment.name,
                data=data, published_url=published_url, project_id=project_id)
            attachment.save()

    def delete_all(self):
        """Deletes all documents for this account!!!"""
        self.stdout.write(
            'Deleting all DocumentCloud documents for account: %s',
             DOCUMENT_CLOUD_ACCOUNT)
        r = self.search('account:%s' % DOCUMENT_CLOUD_ACCOUNT)
        for doc in r:
            self.stdout.write('Deleting document: %s', doc.source)
            doc.delete()
        
    def handle(self, *args, **options):
        logger.info(
            'matterid=%(matter_id)s, all=%(all)s, deleteall=%(deleteall)s',
            options)
        
        try:
            if options['deleteall']:
                answer = input(
                    'Are you sure you want to delete all documents for ' \
                    'account: %s? [Y/n] ' % DOCUMENT_CLOUD_ACCOUNT)
                if answer == '' or answer.lower().startswith('y'):
                    self.delete_all()
                    self.stdout.write('Done\n')
                else:
                    self.stdout.write('Aborting\n')
                return

            matter_id = options['matter_id']
            project = self.get_project(DEFAULT_PROJECT)
            if matter_id:
                logger.info('Fetching files for matter ID %s.', matter_id)
                for attachment in MatterAttachment.objects.filter(
                        matter_id=matter_id):
                    self.fetch(attchment, project.id)
            else:
                q = MatterAttachment.objects.all()
                if options['all']:
                    logger.info('Fetching all files')
                else:
                    logger.info('Fetching new files')
                    q = q.filter(
                        Q(link_obtained_at=None)
                        | Q(link_obtained_at__lte=F('last_modified')))
                for attachment in [a for a in q]:
                    self.fetch(attachment, project.id)
                    attachment.link_obtained_at = timezone.now()
                    attachment.save()
                    logger.debug(
                        'Updated link_obtained_at timestamp for '\
                        'MatterAttachment: %s', attachment.id)
        except Exception as e:
            logger.exception(str(e))
              
        logger.info('Done\n')
        
