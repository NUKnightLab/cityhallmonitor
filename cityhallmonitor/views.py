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
    MatterStatus, MatterType, Subscription, Document

from cityhallmonitor.search import simple_search


def _make_subscription_sid(id, email):
    """Make a subscription identifier (for email)"""
    return "%s-%s" % \
        (str(id), hashlib.md5(email.encode('utf-8')).hexdigest())


def search(request):
    return render(request, 'search.html', context={})

def _documents_json(document_list, is_ranked):
    """
    Return JSON representation of documents
    """
    documents = []
    truncateFlag = False
    documents_qs_count = document_list.count()
    print(documents_qs_count)
    for counter, r in enumerate(document_list):
        if(counter == 1000):
            truncateFlag = True
            break

        attachment = r.matter_attachment
        matter = attachment.matter
        numeric_id,filename = attachment.dc_id.split('-',1)
        documents.append({
            'id': attachment.id,
            'base_thumbnail_url': 'https://assets.documentcloud.org/documents/' + numeric_id + '/pages/' + filename,
            'rank': getattr(r, 'rank', None),
            'sort_date': r.sort_date,
            'name': attachment.name,
            'hyperlink': attachment.hyperlink,
            'dc_id': attachment.dc_id,
            'page_count': attachment.page_count,
            'matter': {
                'id': matter.id,
                'title': matter.title,
                'status': matter.matter_status.name,
                'type': matter.matter_type.name
            }
        })
    return JsonResponse({'error': '', 'is_ranked': is_ranked, 'documents': documents, 
        'truncated': truncateFlag, 'full_count': documents_qs_count})


def default_query(request):
    """
    Find all non-routine documents from within the last 30 days
    """
    try:
        qs, is_ranked = simple_search('', ignore_routine=True, date_range='past-month')
        return _documents_json(qs, is_ranked)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)})


def process_query(request):
    """
    Uses regular expression pattern matching on text for quoted phrases,
    tsquery for the rest.  Uses the soon-to-be deprecated extra()
    method, because this returns a QuerySet on which we can do additional
    filtering.

    We might want to limit the number of results we actually return,
    which is why the query contains an order_by clause.  Returning
    them all for now.
    """

    try:
        raw = request.GET.get('query')
        raw_title = request.GET.get('query_title', '')
        raw_sponsors = request.GET.get('query_sponsors', '')

        ignore_routine = request.GET.get('ignore_routine', 'true').lower() \
            in ['true', 't', '1']
        date_range = request.GET.get('date_range', '')

        if raw_title or raw_sponsors:
            qs, is_ranked = advanced_search(raw, raw_title, raw_sponsors,
                    ignore_routine=ignore_routine,
                    date_range=date_range)
        else:
            qs, is_ranked = simple_search(raw,
                    ignore_routine=ignore_routine,
                    date_range=date_range)

        return _documents_json(qs, is_ranked)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)})


def documents(request, id):
    """View MatterAttachment"""
    try:
        matter_attachment = MatterAttachment.objects.get(pk=id)

        client = DocumentCloud()
        r = client.documents.search('account:%s project:"%s" source: "%s"' % (
            settings.DOCUMENT_CLOUD_ACCOUNT,
            settings.DOCUMENT_CLOUD_PROJECT,
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


def send_notifications_link(request):
    """
    Send user email with link to notifications page
    """
    try:
        email = request.GET.get('email')
        if not email:
            raise Exception('Expected "email" parameter')

        qs = Subscription.objects.filter(email__iexact=email, active=True)
        if not len(qs):
            raise Exception('No active subscriptions found')
        r = qs[0]

        email_template = get_template('email_notifications_link.html')
        html_message = email_template.render({
            'notifications_url': '%s?sid=%s' % ( \
                request.build_absolute_uri(reverse(notifications)),
                _make_subscription_sid(r.id, r.email)
            )
        })

        msg = EmailMessage(
            'City Hall Monitor Manage Notifications',
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            [],
            reply_to=['do-not-reply@knightlab.com'])
        msg.content_subtype = 'html'
        msg.send()

        return JsonResponse({})
    except SMTPException as se:
        traceback.print_exc()
        return JsonResponse({'error': str(se)})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)})


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
            'subscriptions': subscriptions
        })
    except Exception as e:
        traceback.print_exc()
        return render(request, 'notifications.html', context={
            'error': str(e)
        })


def subscribe(request):
    """Save user search subscription and send email"""
    manage_url = activation_url = ''
    try:
        email = request.GET.get('email')
        if not email:
            raise Exception('Expected "email" parameter')
        query = request.GET.get('query')
        if not query:
            raise Exception('Expected "query" parameter')

        email = email.lower()
        query = query.lower()
        r, created = Subscription.objects.get_or_create(email=email, query=query)

        if created or not r.active:
            activation_url = '%s?sid=%s' % (request.build_absolute_uri(reverse(activate)),
                _make_subscription_sid(r.id, email))
        else:
            manage_url = '%s?sid=%s' % (request.build_absolute_uri(reverse(notifications)),
                _make_subscription_sid(r.id, email))

        email_template = get_template('email_subscribe.html')
        html_message = email_template.render({
            'created': created,
            'query': query,
            'activation_url': activation_url,
            'manage_url': manage_url
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
        traceback.print_exc()
        return JsonResponse({'error': str(se)})
    except Exception as e:
        traceback.print_exc()
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
            r.delete()

        return JsonResponse({})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)})
