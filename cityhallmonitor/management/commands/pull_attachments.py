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
        pass

    def handle(self, *args, **options):
        for matter in Matter.objects.filter(
                Q(attachments_obtained_at=None)
                | Q(attachments_obtained_at__lte=F('last_modified')) ):
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
        self.stdout.write('Done')
        
