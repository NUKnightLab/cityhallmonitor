from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from documentcloud import DocumentCloud
import hashlib
from smtplib import SMTPException
from cityhallmonitor.models import Matter, MatterAttachment, \
    MatterStatus, MatterType, Subscription


_subscribe_email_template = """
<p>
You have been subscribed to a search on City Hall Monitor:
</p>
<p>
%(query)s
</p>
<hr>
<a href="%(unsubscribe_url)s?sid=%(sid)s">click here to unsubscribe</a>
"""


def _make_subscription_sid(id, email):
    """Make a subscription identifier (for email)"""
    return "%s-%s" % \
        (str(id), hashlib.md5(email.encode('utf-8')).hexdigest())         


def search(request):
    return render(request, 'search.html', context={})
    
    
def facet(request):
    return render(request, 'facet.html', context={
        'MatterStatuses': MatterStatus.objects\
            .values_list('name', flat=True).order_by('name'),
        'MatterTypes': MatterType.objects\
            .values_list('name', flat=True).order_by('name')
    })
    
    
def documents(request, id):
    """View MatterAttachment"""
    try:    
        matter_attachment = MatterAttachment.objects.get(pk=id) 
        
        client = DocumentCloud()
        r = client.documents.search('account:%s source: "%s"' % (
            settings.DOCUMENT_CLOUD_ACCOUNT, 
            matter_attachment.hyperlink
        ))
        
        if not r:
            raise Exception(
                'Could not find document in DocumentCloud for "%s"' % \
                matter_attachment.hyperlink)
        if len(r) > 1:
            raise Exception(
                'Multiple instances exist in DocumentCloud for "%s"' % \
                matter_attachment.hyperlink)
         
        return render(request, 'documents.html', context={
            'matter_attachment': matter_attachment,
            'doc': r[0]
        })
    except Exception as e:
        return render(request, 'documents.html', context={
            'error': str(e)
        })
        
        
def subscribe(request):
    """Save user search subscription and send email"""
    try:        
        email = request.GET.get('email')
        if not email:
            raise Exception('Expected "email" parameter')
    
        query = request.GET.get('query')
        if not query:
            raise Exception('Expected "query" parameter')
               
        r = Subscription(email=email, query=query)
        r.save()
                
        html_message = _subscribe_email_template % {
            'query': query,
            'unsubscribe_url': request.build_absolute_uri(reverse(unsubscribe)),
            'sid': _make_subscription_sid(r.id, email)
        }
                
        try:          
            send_mail(
                'City Hall Monitor Search Subscription',
                '',
                'KnightLab@northwestern.edu',
                [email],
                fail_silently=False,
                html_message=html_message)
        except SMTPException as se:
            r.delete()
            raise se
                    
        return JsonResponse({})
    except SMTPException as se:
        return JsonResponse({'error': str(se)})
    except Exception as e:
        return JsonResponse({'error': str(e)})


def unsubscribe(request):
    """Delete user search subscription"""
    try:
        sid = request.GET.get('sid')
        if not sid:
            raise Exception('Expected "sid" parameter')    
        id, email_hash = sid.split('-')      
        
        r = Subscription.objects.get(id=id)
        if sid != _make_subscription_sid(id, r.email):
            raise Exception('Invalid search subscription identifier')
            
        r.delete()   
        return render(request, 'unsubscribe.html', context={})
    except ValueError as ve:
        return render(request, 'unsubscribe.html', context={
            'error': 'Malformed subscription identifier'
        })
    except Subscription.DoesNotExist:
        return render(request, 'unsubscribe.html', context={
            'error': 'Search subscription not found'
        })
    except Exception as e:
        return render(request, 'unsubscribe.html', context={
            'error': str(e)
        })
        