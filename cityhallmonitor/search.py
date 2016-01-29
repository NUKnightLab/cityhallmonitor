# consider https://djangosnippets.org/snippets/1328/ for an example of making this work
# as part of a model class
import re
from django.utils import timezone
from cityhallmonitor.models import Document
from datetime import timedelta, datetime

_re_query = re.compile("(\\\".*?\\\"|(?:\s|^)'.*?'(?:\s|$)| )")
_re_phrase = re.compile("^'.*'$|^\".*\"$")


def simple_search(query, ignore_routine=True, date_range=None):

    where, extra_select, order_by, is_ranked = _common_search_setup(query,
    ignore_routine=ignore_routine,
    date_range=date_range)

    qs = Document.objects.defer('text', 'text_vector', 'text_vector_weighted')\
            .extra(select=extra_select, where=where, order_by=[order_by])\
            .select_related('matter_attachment', 'matter_attachment__matter')

    return qs, is_ranked

def _common_search_setup(query, ignore_routine=True, date_range=None):
    """DRY for code in common between advanced and simple"""
    rank_normalization = 32 # default
    order_by='-sort_date'
    is_ranked = False
    where = []
    extra_select = {}
    word_list = []

    pieces = [p.strip() for p in _re_query.split(query) if p.strip()]
    for s in pieces:
        if _re_phrase.match(s):
            s = s.strip("\"'")
            where.append("text_vector_weighted @@ plainto_tsquery('english', '%s') AND text ~* '\m%s\M'" % (s, s))
            word_list.extend(s.split())
        else:
            word_list.append(s.replace("'", "''"))
    if word_list:
        ts_query = "plainto_tsquery('english', '%s')" % ' '.join(word_list)
        where.append("text_vector_weighted @@ %s" % ts_query)
        extra_select['rank'] = 'ts_rank(text_vector, %s, %d )' % (ts_query, rank_normalization)
        # order by rank as long as we have a non-empty query string
        order_by = '-rank'
        is_ranked = True

    if ignore_routine:
        where.append("cityhallmonitor_document.is_routine = false")

    if not (date_range is None or date_range == 'any' or date_range == ''):
        if date_range == 'past-year':
            dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=365)
        elif date_range == 'past-month':
            dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        elif isinstance(date_range, datetime):
            dt = date_range
        else:
            raise Exception('Invalid date_range parameter "%s"' % date_range)

        where.append("sort_date >= '%s'" % dt)

    return where, extra_select, order_by, is_ranked

def advanced_search(query, query_title='', query_sponsors='',
    ignore_routine=True, date_range=None):
    """
    Advanced search using weights in query
    """

    where, extra_select, order_by, is_ranked = _common_search_setup(query,
    ignore_routine=ignore_routine,
    date_range=date_range)

    if query_title:
        pieces = ['%s:A' % p.replace("'", "''") for p in query_title.split()]
        ts_query = "to_tsquery('english', '%s')" % ' & '.join(pieces)
        where.append("text_vector_weighted @@ %s" % ts_query)

    if query_sponsors:
        pieces = ['%s:B' % p.replace("'", "''") for p in query_sponsors.split()]
        ts_query = "to_tsquery('english', '%s')" % ' & '.join(pieces)
        where.append("text_vector_weighted @@ %s" % ts_query)

    qs = Document.objects.defer('text', 'text_vector', 'text_vector_weighted')\
            .extra(select=extra_select, where=where, order_by=[order_by])\
            .select_related('matter_attachment', 'matter_attachment__matter')

    return qs, is_ranked

def subscription_search(subscription):
    """Callers are responsible for updating `last_check`"""
    qs, is_ranked = simple_search(subscription.query, date_range=subscription.last_check)
    return qs
