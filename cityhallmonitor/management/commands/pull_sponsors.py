from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone
import json
import logging
import requests
from cityhallmonitor.models import Matter, MatterSponsor


logger = logging.getLogger(__name__)

_legistar_matter_sponsors_url = \
    'http://webapi.legistar.com/v1/chicago/Matters/%(matter_id)s/Sponsors'


class Command(BaseCommand):
    help = 'Get sponsors for updated matters from the Chicago Legistar API.'

    def add_arguments(self, parser):
        parser.add_argument('matter_id', nargs='?', help='Matter ID')

    def fetch(self, matter):
        """Fetch sponsors for matter"""
        url = _legistar_matter_sponsors_url % { 'matter_id': matter.id }
        logger.debug('Downloading %s' % url)
        
        headers = {'Accept': 'text/json'}
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise Exception('Error downloading %s [%d]' \
                % (url, r.status_code))
        for i, item in enumerate(r.json()):
            try:
                if item['MatterSponsorNameId']:
                    r = MatterSponsor.from_json(item)
                    r.save()
            except Exception as e:
                logger.info(item)
                raise e
                
        matter.sponsors_obtained_at = timezone.now()
        matter.save()

    def handle(self, *args, **options):
        logger.info('matter_id=%(matter_id)s' % options)

        try:
            matter_id = options['matter_id']
            if matter_id:
                logger.info(
                    'Fetching sponsors for matter ID %s', matter_id)
                matter = Matter.objects.get(id=matter_id)
                self.fetch(matter)
            else:
                logger.info(
                    'Fetching all updated matter sponsors.')
            
                for matter in Matter.objects.filter(
                        Q(sponsors_obtained_at=None)
                        | (Q(sponsors_obtained_at__lte=F('last_modified'))
                         & Q(last_modified__isnull=False))):
                    self.fetch(matter)
        except Exception as e:
            logger.exception(str(e))
        
        logger.info('Done\n')
         
