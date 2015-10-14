import hashlib
import traceback
from smtplib import SMTPException
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils import timezone
from documentcloud import DocumentCloud
from cityhallmonitor.models import Matter, MatterAttachment, \
    MatterStatus, MatterType, Subscription

    
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
 
 
def _get_subscription(sid):
    """
    Validate subscription identifier and return associated record
    """
    try:
        id, email_hash = sid.split('-')      
            
        r = Subscription.objects.get(id=id)
        if sid != _make_subscription_sid(id, r.email):
            raise Exception('Invalid subscription identifier')
        
        return r
    except ValueError as ve:
        raise Exception('Malformed subscription identifier')
    except Subscription.DoesNotExist:
        raise Exception('Subscription not found')


def notifications(request):
    """
    Manage notifications view
    """
    try:
        sid = request.GET.get('sid')
        if not sid:
            raise Exception('Expected "sid" parameter')   
                       
        r = _get_subscription(sid)
                 
        subscriptions = []
        for d in Subscription.objects.filter(email=r.email, active=True).values():
            d['sid'] = _make_subscription_sid(d['id'], d['email'])
            subscriptions.append(d)
            
        return render(request, 'notifications.html', context={
            'email': r.email,
            'sid': sid, 
            'subscriptions': subscriptions
        })
    except Exception as e:
        traceback.print_exc()
        return render(request, 'notifications.html', context={
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
 
        r = Subscription(email=email, query=query, 
            last_check=timezone.now())
        r.save()
     
        email_template = get_template('email_subscribe.html')
        html_message = email_template.render({
            'query': query,
            'activation_url': '%s?sid=%s' % ( \
                request.build_absolute_uri(reverse(activate)),
                _make_subscription_sid(r.id, email)
            )
        })
                        
        try:          
            msg = EmailMessage(
                'City Hall Monitor Search Subscription', 
                html_message,
                settings.DEFAULT_FROM_EMAIL, 
                [email], 
                [],
                reply_to=['do-not-reply@knightlab.com'])
            msg.content_subtype = 'html'
            msg.send()
        except SMTPException as se:
            r.delete()
            raise se
                    
        return JsonResponse({})
    except SMTPException as se:
        return JsonResponse({'error': str(se)})
    except Exception as e:
        return JsonResponse({'error': str(e)})


def activate(request):
    """Activate user search subscription"""
    try:
        sid = request.GET.get('sid')
        if not sid:
            raise Exception('Expected "sid" parameter')   
  
        r = _get_subscription(sid)
        r.active = True
        r.save()
        
        return render(request, 'activate.html', context={
            'notifications_url': '%s?sid=%s' % ( \
                request.build_absolute_uri(reverse(notifications)), 
                _make_subscription_sid(r.id, r.email)
            )
        })
    except Exception as e:
        traceback.print_exc()
        return render(request, 'activate.html', context={
            'error': str(e)
        })

        
def unsubscribe(request):
    """Delete user search subscriptions"""
    try:
        sid_list = request.GET.getlist('sids[]')
        if not sid_list:
            raise Exception('Expected "sids[]"')
        
        for sid in sid_list:
            r = _get_subscription(sid)                
            #r.delete()   
            print('fake delete', r.id) 
 
        return JsonResponse({})
    except Exception as e:
        return JsonResponse({'error': str(e)})
       
