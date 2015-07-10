from django.core.management.base import BaseCommand, CommandError
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
        # Check data type
        data_type = options['data_type']       
        if not data_type in _data_type_to_api:
            raise CommandError('Unsupported data type "%s"' % data_type)
            
        # Find Model class
        model_class_name = 'cityhallmonitor.models.%s' % data_type
        model_class = pydoc.locate(model_class_name)
        if not model_class:
            raise CommandError('Could not find Model "%s"' % model_class_name)
           
        # Pull data         
        url = '%s/%s' % (_legistar_url, _data_type_to_api[data_type])       
        self.stdout.write('Downloading %s...' % url)   
     
        headers = {'Accept': 'text/json'}
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise Exception('Error downloading %s [%d]' \
                % (url, r.status_code))
        
        item_list = r.json()
        n = len(item_list)
         
        for i, item in enumerate(item_list[51100:]):
            try:
                r = model_class.from_json(item)
                r.save()
            except TypeError as e:
                print(item)
                raise e
            
            if i % 100 == 0:
                print('Processed %d/%d records...' % (i, n))
                
                    
        self.stdout.write('Done')
        
