import logging
from django.core.management.base import BaseCommand
from cityhallmonitor.models import Document

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'For each document, force an update of its related fields and its postgres text index'

    logger.info('Rebuilding text index')
    
    def handle(self, *args, **options):
        for i,d in enumerate(Document.objects.all()):
            d._set_dependent_fields()
            d.save(update_text=True)
            if i % 1000 == 0:
                logger.debug("Processed %i documents" % i)
        logger.info('Done\n')
