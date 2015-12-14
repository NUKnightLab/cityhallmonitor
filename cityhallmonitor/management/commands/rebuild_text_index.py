import logging
from django.core.management.base import BaseCommand
from cityhallmonitor.models import Document

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'For each document, force an update of its related fields and its postgres text index'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, 
            help='Process up to LIMIT documents')
        parser.add_argument('--where', 
            help='WHERE condition to filter documents')

    def handle(self, *args, **options):
        logger.info(
            'Rebuilding text index, limit=%(limit)s, where="%(where)s"' \
            % options)
        
        if options['where']:
            qs = Document.objects.extra(where=[options['where']])
        else:
            qs = Document.objects.all()
            
        if options['limit']:
            qs = qs[:options['limit']]
        
        for i,d in enumerate(qs, start=1):
            d._set_dependent_fields()
            d.save(update_text=True)
            if i % 1000 == 0:
                logger.debug("Processed %i documents" % i)
        
        logger.info('Done, processed %d documents\n' % i)
