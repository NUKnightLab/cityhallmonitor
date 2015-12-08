from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.utils import timezone
import json
import logging
import pydoc
import requests


logger = logging.getLogger(__name__)

_legistar_url = 'http://webapi.legistar.com/v1/chicago'

# Map data_type to API call suffix
_data_type_to_api = {
    'Body':         'Bodies',
    'BodyType':     'BodyTypes',
    'Matter':       'Matters',
    'MatterStatus': 'MatterStatuses',
    'MatterType':   'MatterTypes',
    'Person':       'Persons'
}

class Command(BaseCommand):
    help = 'Pull data from the Chicago Legistar API.'

    def add_arguments(self, parser):
        parser.add_argument('data_type',
            help=', '.join(sorted(_data_type_to_api.keys())))
        parser.add_argument('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Pull all data items, regardless of modification date')

    def handle(self, *args, **options):
        logger.info('data_type=%(data_type)s, all=%(all)s' % options)
        
        try:                        
            # Check data type
            data_type = options['data_type']       
            if not data_type in _data_type_to_api:
                raise CommandError('Unsupported data type "%s"' % data_type)
             
            # Find model class
            model_class_name = 'cityhallmonitor.models.%s' % data_type
            model_class = pydoc.locate(model_class_name)
            if not model_class:
                raise CommandError('Could not find Model "%s"' % model_class_name)
        
            # Set filter?
            filter = ''
            if not options['all']:
                d = model_class.objects.aggregate(Max('last_modified'))   
                if  d['last_modified__max']:
                    filter = "&$filter=%sLastModifiedUtc eq null or %sLastModifiedUtc gt datetime'%s'" % (
                        data_type, data_type, d['last_modified__max'].strftime('%Y-%m-%dT%H:%M:%S.%f'))
        
            logger.info('filter=%s', filter)
                    
            # Can never get more than 1000 records at a time
            url_format = '%s/%s?$top=1000&$skip=%%d&$orderby=%sLastModifiedUtc%s' \
                % (_legistar_url, _data_type_to_api[data_type], data_type, filter)
                        
            skip = 0
          
            while True:
                url = url_format % skip
                   
                headers = {'Accept': 'text/json'}
                r = requests.get(url, headers=headers)
                if not r.ok:
                    raise Exception('Error downloading %s [%d]' \
                        % (url, r.status_code))
        
                item_list = r.json()
                n = len(item_list)
            
                for item in item_list:
                    try:
                        r = model_class.from_json(item)
                        r.save()
                    except Exception as e:
                        logger.info(repr(item))
                        raise e
                                                         
                skip += n
                if n < 1000:
                    break
            
                logger.info('Processed %d records' % skip)
       
            logger.info('Processed %d records' % skip)                           
        except Exception as e:
            logger.exception(str(e))
            
        logger.info('Done\n')
       
