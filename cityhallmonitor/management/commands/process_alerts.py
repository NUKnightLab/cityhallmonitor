from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from cityhallmonitor.models import Subscription
from documentcloud import DocumentCloud


DEFAULT_PROJECT = 'Chicago City Hall Monitor'

EMAIL_SUBJECT = 'City Hall Monitor Search Alert'

EMAIL_FROM = 'KnightLab@northwestern.edu'

EMAIL_TEMPLATE = """
<p>You alert subscription on City Hall Monitor:
</p>
<p>%(query)s
</p>
<p>Matched %(n)d new documents:</p>
"""

EMAIL_DOC_TEMPLATE = """
<p>%(matter)s<br>
<a href="%(link_url)s">%(link_text)s</a>
</p>
"""


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
        """Send user subscription alert"""
        n_documents = len(document_list)
        
        html_message = EMAIL_TEMPLATE % ({
            'query': subscription.query,
            'n': n_documents
        })               
        for doc in document_list:
            html_message += EMAIL_DOC_TEMPLATE % {
                'matter': doc.data['MatterTitle'],
                'link_url': doc.published_url,
                'link_text': doc.title
            }
        
        print('Sending alert for %d documents [%s]' % (
            n_documents, subscription))      
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
        
