import re
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.utils import timezone
from cityhallmonitor import search
from cityhallmonitor.models import Subscription, Document
from cityhallmonitor.views import _make_subscription_sid
from smtplib import SMTPException
from django.conf import settings

ATTACHMENT_PUBLISH_URL = settings.DOMAIN_URL + '/documents/%d'

EMAIL_SUBJECT = 'City Hall Monitor Search Alert'

EMAIL_TEMPLATE = 'email_alert.html'

_re_query = re.compile("(\\\".*?\\\"|(?:\s|^)'.*?'(?:\s|$)| )")
_re_phrase = re.compile("^'.*'$|^\".*\"$")


class Command(BaseCommand):
    help = 'Process user subscriptions.'
    _notifications_url = ''

    def add_arguments(self, parser):
        pass # noop

    def search(self, subscription):
        """
        Return search results from our database
        """

        documents = []
        for r in search.subscription_search(subscription):
            attachment = r.matter_attachment
            matter = attachment.matter

            documents.append({
                'published_url': ATTACHMENT_PUBLISH_URL % attachment.id,
                'matter_title': matter.title,
                'name': attachment.name
            })

        return documents

    def send_subscription_alert(self, subscription, documents):
        """
        Send user subscription alert email
        """
        email_template = get_template(EMAIL_TEMPLATE)

        html_message = email_template.render({
            'query': subscription.query,
            'notifications_url': '%s?sid=%s' % ( \
                self._notifications_url,
                _make_subscription_sid(subscription.id, subscription.email)
            ),
            'documents': documents
        })

        self.stdout.write('Sending alert for %d documents [%s]' % \
            (len(documents), subscription))

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
        """
        Process subscription
        """
        documents = self.search(subscription)

        try:
            if len(documents):
                self.send_subscription_alert(subscription, documents)

            subscription.last_check = timezone.now()
            subscription.save()
        except SMTPException as se:
            self.stdout.write(
                'ERROR sending email for subscription %d: %s' % \
                (subscription.id, str(se)))

    def handle(self, *args, **options):
        self._notifications_url = \
            settings.DOMAIN_URL + reverse('notifications')
        self.stdout.write('Notifications URL = %s' % self._notifications_url)

        subscription_list = Subscription.objects.filter(active=True)
        self.stdout.write('Processing %d subscriptions' % len(subscription_list))

        for subscription in subscription_list:
            self.process_subscription(subscription)

        self.stdout.write('Done')
