from django.core.management.base import BaseCommand, CommandError
import json
from cityhallmonitor.models import Action

class Command(BaseCommand):
    help = 'Import Action data from JSON file'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('path', nargs='?')

    def handle(self, *args, **options):
        from django.db import IntegrityError
                
        self.stdout.write('Loading %s...' % options['path'])        
        with open(options['path'], 'r') as fp:
            data = json.load(fp)
        
        self.stdout.write('Processing %d records...' % len(data))        
        for d in data:
            r = Action.from_json(d)
            r.save()
             
        self.stdout.write('Done')
        
