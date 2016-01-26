import logging
import pprint
import re
import urllib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
from cityhallmonitor.models import Matter, MatterAttachment
from documentcloud import DocumentCloud


logger = logging.getLogger(__name__)

DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT
DOCUMENT_CLOUD_PROJECT = settings.DOCUMENT_CLOUD_PROJECT

ATTACHMENT_PUBLISH_URL = 'https://cityhallmonitor.knightlab.com/documents/%d'

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
            self._client = DocumentCloud(
                settings.DOCUMENT_CLOUD_USERNAME,
                settings.DOCUMENT_CLOUD_PASSWORD)
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
        r = self.client().documents.search(query)
        assert type(r) is list, \
            'DocumentCloud search response is %s: %s' % (type(r), repr(r))
        return r

    def fetch(self, attachment, project_id):
        """Upload attachment file to DocumentCloud"""
        r = self.search('account:%s project:"%s" source: "%s"' % (
                DOCUMENT_CLOUD_ACCOUNT,
                DOCUMENT_CLOUD_PROJECT,
                attachment.hyperlink))

        logger.debug('Result from DocumentCloud is %s' % str(r))

        if r:
            logger.debug(
                'Document exists in DocumentCloud. Not transferring: %s',
                attachment.hyperlink)

            if len(r) > 1:
                raise DocumentSyncException(
                    'Multiple instances exist in DocumentCloud for '\
                    'document: %s' % attachment.hyperlink)
        else:
            logger.info('Transferring to DocumentCloud: %s',
                attachment.hyperlink)

            data = {
                'MatterAttachmentId': str(attachment.id),
                'MatterId': str(attachment.matter.id),
                'ops:DescriptionProcessed': '0'
            }
            published_url = ATTACHMENT_PUBLISH_URL % attachment.id
            doc = self.upload_to_doccloud(
                attachment.hyperlink,
                attachment.name,
                data=data,
                project_id=project_id,
                published_url=published_url)

            attachment.link_obtained_at = timezone.now()
            attachment.dc_id = doc.id
            attachment.save()
            logger.debug(
                'Updated link_obtained_at timestamp for '\
                'MatterAttachment: %s', attachment.id)

    def delete_all(self):
        """Deletes all documents for this account!!!"""
        self.stdout.write(
            'Deleting all DocumentCloud documents for account:%s project:"%s"',
             DOCUMENT_CLOUD_ACCOUNT, DOCUMENT_CLOUD_PROJECT)
        r = self.search('account:%s project:"%s"' % (
            DOCUMENT_CLOUD_ACCOUNT, DOCUMENT_CLOUD_PROJECT))
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
                    'account:%s project:"%s"? [Y/n] ' % (
                    DOCUMENT_CLOUD_ACCOUNT, DOCUMENT_CLOUD_PROJECT))
                if answer == '' or answer.lower().startswith('y'):
                    self.delete_all()
                    self.stdout.write('Done\n')
                else:
                    self.stdout.write('Aborting\n')
                return

            project = self.get_project(DOCUMENT_CLOUD_PROJECT)

            q = MatterAttachment.objects.all()

            if options['all']:
                logger.info('Fetching all files')
            elif options['matter_id']:
                logger.info('Fetching files for matter ID %s', options['matter_id'])
                q = q.filter(matter_id=options['matter_id'])
            else:
                logger.info('Fetching new files')
                q = q.filter(link_obtained_at=None)

            for attachment in [a for a in q]:
                self.fetch(attachment, project.id)
        except Exception as e:
            logger.exception(str(e))

        logger.info('Done\n')
