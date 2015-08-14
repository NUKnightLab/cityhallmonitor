from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
import json
import pydoc
import requests
from cityhallmonitor.models import Matter, MatterSponsor

_legistar_matter_sponsors_url = \
    'http://webapi.legistar.com/v1/chicago/Matters/%(matter_id)s/Sponsors'


class Command(BaseCommand):
    help = 'Get sponsors for updated matters from the chicago legistar API.'

    def add_arguments(self, parser):
        parser.add_argument('matter_id', nargs='?', help='Matter ID')

    def fetch(self, matter):
        url = _legistar_matter_sponsors_url % { 'matter_id': matter.id }
        self.stdout.write('Downloading %s...' % url)   
        headers = {'Accept': 'text/json'}
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise Exception('Error downloading %s [%d]' \
                % (url, r.status_code))
        for i, item in enumerate(r.json()):
            try:
                r = MatterSponsor.from_json(item)
                r.save()
            except TypeError as e:
                print(item)
                raise e
        matter.sponsors_obtained_at = timezone.now()
        matter.save()

    def handle(self, *args, **options):
        matter_id = options['matter_id']
        if matter_id:
            self.stdout.write(
                'Fetching sponsors for matter ID %s.' % matter_id)
            matter = Matter.objects.get(id=matter_id)
            self.fetch(matter)
        else:
            self.stdout.write('Fetching all updated matter sponsors.')
            for matter in Matter.objects.filter(
                    Q(sponsors_obtained_at=None)
                    | Q(sponsors_obtained_at__lte=F('last_modified')) ):
                self.fetch(matter)
        self.stdout.write('Done')
        
