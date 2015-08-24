from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
import json
import pydoc
import requests
from cityhallmonitor.models import Matter, MatterAttachment

_legistar_matter_attachments_url = \
    'http://webapi.legistar.com/v1/chicago/Matters/%(matter_id)s/Attachments'
API_DATA_TYPE = 'MatterAttachments'


class Command(BaseCommand):
    help = 'Get attachments for updated matters from the chicago legistar API.'

    def add_arguments(self, parser):
        parser.add_argument('matter_id', nargs='?', help='Matter ID')

    def fetch(self, matter):
        url = _legistar_matter_attachments_url % { 'matter_id': matter.id }
        self.stdout.write('Downloading %s...' % url)   
        headers = {'Accept': 'text/json'}
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise Exception('Error downloading %s [%d]' \
                % (url, r.status_code))
        for i, item in enumerate(r.json()):
            try:
                r = MatterAttachment.from_json(matter.id, item)
                r.save()
            except TypeError as e:
                print(item)
                raise e
        matter.attachments_obtained_at = timezone.now()
        matter.save()

    def handle(self, *args, **options):
        try:
            matter_id = options['matter_id']
            if matter_id:
                self.stdout.write(
                    '%s Fetching attachments for matter ID %s.' \
                    % (timezone.now(), matter_id))
                matter = Matter.objects.get(id=matter_id)
                self.fetch(matter)
            else:
                self.stdout.write(
                    '%s Fetching all updated matter attachments.' \
                    % timezone.now())
                for matter in Matter.objects.filter(
                        Q(attachments_obtained_at=None)
                        | Q(attachments_obtained_at__lte=F('last_modified')) ):
                    self.fetch(matter)
            self.stdout.write('%s Done' % timezone.now())
        except Exception as e:
            self.stdout.write('ERROR: %s %s' % (type(e), str(e)))
            self.stdout.write('%s Ending'  % timezone.now())
                  
