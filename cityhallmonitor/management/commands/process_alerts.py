from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.utils import timezone
from cityhallmonitor.models import Subscription
from documentcloud import DocumentCloud


DEFAULT_PROJECT = 'Chicago City Hall Monitor'

EMAIL_SUBJECT = 'City Hall Monitor Search Alert'

EMAIL_FROM = 'KnightLab@northwestern.edu'

EMAIL_TEMPLATE = 'email_alert.html'


class Command(BaseCommand):
    help = 'Process user alert subscriptions.'
    _client = None

    def client(self):
        """Using un-authenticated client..."""
        if self._client is None:
            self._client = DocumentCloud()
        return self._client

    def add_arguments(self, parser):
        pass # noop

    def search(self, query):
        return self.client().documents.search(query)

    def send_subscription_alert(self, subscription, document_list):
        """Send user subscription alert email"""
        email_template = get_template(EMAIL_TEMPLATE)
        
        html_message = email_template.render({
            'query': subscription.query,
            'documents': document_list
        })               
        
        print('Sending alert for %d documents [%s]' % (
            len(document_list), subscription))      
        send_mail(
            EMAIL_SUBJECT,
            '',
            EMAIL_FROM,
            [subscription.email],
            fail_silently=False,
            html_message=html_message)
       
    def process_subscription(self, subscription):
        """Process subscription"""
        query = 'account:%s project:"%s" %s' % (
            settings.DOCUMENT_CLOUD_ACCOUNT, 
            DEFAULT_PROJECT, 
            subscription.query)
        print(query)
 
        r = self.search(query)
        if subscription.last_check:
            r = [d for d in r if d.updated_at > subscription.last_check]
         
        try:
            if len(r):
                self.send_subscription_alert(subscription, r)
                        
            subscription.last_check = timezone.now()
            subscription.save()
        except SMTPException as se:
            self.stdout.write(
                'ERROR sending email for subscription %d: %s' % \
                (subscription.id, str(se)))                             
        
    def handle(self, *args, **options):
        """Process subscriptions"""
        subscription_list = Subscription.objects.all()
        print('Processing %d subscriptions' % len(subscription_list))

        for subscription in subscription_list:  
            self.process_subscription(subscription)         

        self.stdout.write('Done')
        
