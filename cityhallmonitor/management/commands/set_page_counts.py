from cityhallmonitor.models import MatterAttachment
from django.core.management.base import BaseCommand, CommandError
import requests
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Lookup record by id or hyperlink/source and compare with DocumentCloud'

    def add_arguments(self, parser):
        parser.add_argument('--count', action='store', type=int,
            help='If specified, only process n documents which need page numbers. If missing, do all of them.')

    def handle(self, *args, **options):
        qs = MatterAttachment.objects.filter(page_count__isnull=True,document__isnull=False).order_by('-document__sort_date')
        print("%i documents need page counts" % qs.count())
        if options['count'] and options['count'] < qs.count():
            print("But only processing %i at your request" % options['count'])
        for i,ma in enumerate(qs):
            if options['count'] and i >= options['count']:
                print("Stopping at %(count)s as requested" % options)
                break
            resp = requests.get(ma.dc_json_url)
            if resp.ok:
                data = resp.json()
                ma.page_count = data['document']['pages']
                ma.save()
            else:
                logger.warn("Error getting JSON for {}: {} {}".format(ma.dc_id, resp.status_code, resp.reason))
            if i % 1000 == 0: print("processed {}".format(i))
