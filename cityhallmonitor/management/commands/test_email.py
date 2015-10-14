from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage


EMAIL_SUBJECT = 'City Hall Monitor Email Test'

EMAIL_MESSAGE = 'This is a test of City Hall Monitor email.'


class Command(BaseCommand):
    help = 'Test sending of email via SES.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('recipient',
            help='Email address of recipient'
        )

    def handle(self, *args, **options):
        print(args)
        print(options)
        
        # Check data type
        recipient = options['recipient']       
        if not recipient:
            raise CommandError('You must specify a recipient')
           
        self.stdout.write('Sending email to "%s"' % recipient)

        msg = EmailMessage(
            EMAIL_SUBJECT,
            EMAIL_MESSAGE,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            [],
            reply_to=['do-not-reply@knightlab.com'])
        msg.content_subtype = 'html'
        msg.send()
                    
        self.stdout.write('Done')
        
