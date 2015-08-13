from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail


_email_subject = 'City Hall Monitor Test'

_email_from = 'KnightLab@northwestern.edu'

_email_message = 'This is a test of City Hall Monitor email.'


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
           
        self.stdout.write('Sending email to "%s"...' % recipient)
                 
        send_mail(_email_subject, _email_message, _email_from, 
            [recipient], fail_silently=False)
                    
        self.stdout.write('Done')
        
