from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
import json
import requests
from cityhallmonitor.models import Event, EventItem

# param is EventId
_legistar_url = 'http://webapi.legistar.com/v1/chicago/Events/%d/EventItems?AgendaNote=1&MinutesNote=1'

class Command(BaseCommand):
    help = 'Pull EventItem data for every saved Event from chicago legistar API.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):       
        headers = {'Accept': 'text/json'}
        
        q_events = Event.objects.all()
        n = len(q_events)
        
        for i, event in enumerate(q_events):
            url = _legistar_url % event.id            
            r = requests.get(url, headers=headers)
            if not r.ok:
                raise CommandError('Error downloading %s [%d]' \
                    % (url, r.status_code))
        
            item_list = r.json()
        
            for item in item_list:
                r = EventItem.from_json(item)
                r.save()
            
            if i % 50 == 0:
                self.stdout.write('Processed %d/%d events' % (i, n))
                    
        self.stdout.write('Done')
        
