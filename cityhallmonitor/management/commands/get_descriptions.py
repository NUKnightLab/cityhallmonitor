import re
import urllib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from documentcloud import DocumentCloud
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
        query = 'account:%s' % DOCUMENT_CLOUD_ACCOUNT
        if not options['all']:
            query += ' ops:DescriptionProcessed: 0' 
        r = self.search(query)
        for doc in r:
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
            self.stdout.write(doc.source)
