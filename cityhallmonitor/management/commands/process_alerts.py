from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.utils import timezone
from cityhallmonitor.models import Subscription
from cityhallmonitor.views import _make_subscription_sid
from documentcloud import DocumentCloud
from smtplib import SMTPException


DEFAULT_PROJECT = 'Chicago City Hall Monitor'

EMAIL_SUBJECT = 'City Hall Monitor Search Alert'

EMAIL_TEMPLATE = 'email_alert.html'


class Command(BaseCommand):
    help = 'Process user subscriptions.'
    _client = None
    _notifications_url = ''

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
            'notifications_url': '%s?sid=%s' % ( \
                self._notifications_url,
                _make_subscription_sid(subscription.id, subscription.email)
            ),
            'documents': document_list
        })               
        
        self.stdout.write('Sending alert for %d documents [%s]' % \
            (len(document_list), subscription))  
                               
        msg = EmailMessage(
            EMAIL_SUBJECT,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [subscription.email],
            [],
            reply_to=['do-not-reply@knightlab.com'])
        msg.content_subtype = 'html'
        msg.send()

    def process_subscription(self, subscription):
        """Process subscription"""
        query = 'account:%s project:"%s" %s' % (
            settings.DOCUMENT_CLOUD_ACCOUNT, 
            DEFAULT_PROJECT, 
            subscription.query)
 
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
        self._notifications_url = \
            settings.DOMAIN_URL + reverse('notifications')
        self.stdout.write('Notifications URL = %s' % self._notifications_url)
        
        subscription_list = Subscription.objects.filter(active=True)
        self.stdout.write('Processing %d subscriptions' % len(subscription_list))

        for subscription in subscription_list:  
            self.process_subscription(subscription)         

        self.stdout.write('Done')
        
