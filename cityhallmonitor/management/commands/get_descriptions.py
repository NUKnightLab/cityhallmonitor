import re
import sys
import urllib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from documentcloud import DocumentCloud
from cityhallmonitor.models import MatterAttachment
from newspaper.nlp import summarize

API_DATA_TYPE = 'MatterAttachments'
USERNAME = settings.DOCUMENT_CLOUD_USERNAME
PASSWORD = settings.DOCUMENT_CLOUD_PASSWORD
DOCUMENT_CLOUD_ACCOUNT = settings.DOCUMENT_CLOUD_ACCOUNT
ATTACHMENT_PUBLISH_URL = 'https://cityhallmonitor.knightlab.com/documents/%d'
DEFAULT_PROJECT = 'Chicago City Hall Monitor'
PARENTHETICALS = re.compile('[{([})\]"]+')

class Command(BaseCommand):
    help = 'Get PDF links for new/updated attachments from the chicago legistar API.'
    _client = None

    def client(self):
        if self._client is None:
            self._client = DocumentCloud(USERNAME, PASSWORD)
        return self._client

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true',
            help='Process all attachments.')
        parser.add_argument('--delerr', action='store_true', help=\
            'Delete documents with error status and mark for re-processing')
        parser.add_argument('--force', action='store_true', help=\
            'With --delerr: force deletion of error status documents when ' \
            'MatterAttachment does not exist on this system. Creates a ' \
            'potential synchronization issue with the system that uploaded ' \
            'the document. Should be followed by pull_pdfs --all.')

    def search(self, query):
        return DocumentCloud(USERNAME, PASSWORD).documents.search(query)

    def cleanup(self, text):
        if text.startswith('b"') or text.startswith("b'"):
            text = text[2:]
        text = text.replace('\\\\', '')
        text = text.replace("\\'", "'")
        text = ' '.join([t for t in text.split(' ')
            if (len(t) > 1 or t.isalnum())
            and '\\x' not in t
            and '<' not in t
            and '>' not in t
            and '^' not in t
            and not PARENTHETICALS.findall(t.strip('{([})]"'))
        ])
        return text

    def handle(self, *args, **options):
        if options['force']:
            if options['delerr']:
                self.stdout.write(
                    '\nWARNING: documents with error status that do not have ' \
                    'a MatterAttachment on the local system will be ' \
                    'deleted. This will potentially create a condition on ' \
                    'the system where the document was upload in which the ' \
                    'document is marked as processed but does not exist in ' \
                    'DocumentCloud. To resolve this condition, AFTER THIS RUN '\
                    'either\n\n' \
                    '  1. On the conflicting system run:\n\n' \
                    '     pull_pdfs --all\n\n' \
                    '    or\n\n' \
                    '  2. Locally run:\n\n' \
                    '     pull_data Matter\n' \
                    '     pull_attachments\n' \
                    '     pull_pdfs\n\n')
                input_ = input('Continue with forced delete? (Y/n) ')
            if not options['delerr']:
                input_ = input(
                    '\nINFO: --force is non-operational without --delerr\n\n' \
                    'Continue without forced delete? (Y/n) ')
            if input_ and not input_.lower().startswith('y'):
                self.stdout.write('Aborting ...')
                sys.exit(0)
        query = 'account:%s' % DOCUMENT_CLOUD_ACCOUNT
        if not options['all']:
            query += ' ops:DescriptionProcessed: 0' 
        r = self.search(query)
        for doc in r:
            if doc.access == 'error':
                if options['delerr']:
                    try:
                        doc_obj = MatterAttachment.objects.get(
                            id=int(doc.data['MatterAttachmentId']))
                        doc_obj.link_obtained_at = None
                        self.stdout.write('Document with error status will ' \
                            'be marked as unprocessed: %s' % (doc.source))
                        doc_obj.save()
                        doc.delete()
                    except MatterAttachment.DoesNotExist:
                        if options['force']:
                            self.stdout.write('WARNING: forcing delete of ' \
                            'document with error status. Be sure to resolve ' \
                            'synchronization after this run. %s' % doc.source)
                        else:
                            self.stdout.write('MatterAttachment for ' \
                            'document with error status does not exist on ' \
                            'this system. Document will not be deleted. Run ' \
                            'description processing with --delerr on other ' \
                            'system to purge documents with error ' \
                            'status or update Matters, MatterAttachments and ' \
                            'PDFs on the local system: %s' % doc.source)
                else:
                    self.stdout.write('SKIPPING: description processing of '
                    'document with error status. %s' % doc.source)
                continue
            elif doc.access == 'pending':
                self.stdout.write('SKIPPING: description processing of ' \
                    'pending document: %s' % doc.source)
            elif doc.access == 'public':
                text = str(doc.full_text).replace('\\n', ' ')
                text = self.cleanup(text)
                summary = ' '.join(
                    summarize(text=text, title=doc.data['MatterTitle']))
                if len(summary) < 20:
                    summary = ' '.join(text.split(' ')[:100])
                doc.description = summary
                try:
                    del(doc.data['ops:DescriptionProcessed'])
                except KeyError:
                    pass # if we use --all this key might not be there
                doc.put()
                self.stdout.write('Description written: %s' % doc.source)
            else:
                self.stdout.write('WARNING: skipping document with ' \
                'unknown status %s: %s' % (doc.access, doc.source))
