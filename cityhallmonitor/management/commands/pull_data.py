from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.utils import timezone
import json
import pydoc
import requests

_legistar_url = 'http://webapi.legistar.com/v1/chicago'

# Map data_type to API call suffix
_data_type_to_api = {
    'Action':       'Actions',
    'Body':         'Bodies',
    'BodyType':     'BodyTypes',
    'Event':        'Events',
    'Matter':       'Matters',
    'MatterStatus': 'MatterStatuses',
    'MatterType':   'MatterTypes',
    'Person':       'Persons',
    'VoteType':     'VoteTypes'
}

class Command(BaseCommand):
    help = 'Do basic data pull from the chicago legistar API.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('data_type', nargs='?',
            help=', '.join(sorted(_data_type_to_api.keys()))
        )

    def handle(self, *args, **options):
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
        
            # Set filter only if there is a max modification date
            filter = ''
            d = model_class.objects.aggregate(Max('last_modified'))   
            if  d['last_modified__max']:
                filter = "&$filter=%sLastModifiedUtc eq null or %sLastModifiedUtc gt datetime'%s'" % (
                    data_type, data_type, d['last_modified__max'].strftime('%Y-%m-%dT%H:%M:%S.%f'))
        
            self.stdout.write('%s %s' % (timezone.now(), filter or '[no filter]'))
        
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
                        self.stdout.write(repr(item))
                        raise e
                                                         
                skip += n
                if n < 1000:
                    break
            
                self.stdout.write('Processed %d records' % skip)
       
            self.stdout.write('Processed %d records' % skip)                           
            self.stdout.write('%s Done' % timezone.now())
        
        except Exception as fe:
            self.stdout.write('ERROR: %s %s' % (type(fe), str(fe)))
            self.stdout.write('%s Ending'  % timezone.now())
            
        
