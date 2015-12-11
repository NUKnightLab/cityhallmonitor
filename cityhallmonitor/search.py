import re
from django.utils import timezone
from cityhallmonitor.models import Document
from datetime import timedelta

_re_query = re.compile("(\\\".*?\\\"|(?:\s|^)'.*?'(?:\s|$)| )")
_re_phrase = re.compile("^'.*'$|^\".*\"$")

def simple_search(query, ignore_routine=True, date_range=None):
    where = []
    word_list = []
    pieces = [p.strip() for p in _re_query.split(query) if p.strip()]

    for s in pieces:
        if _re_phrase.match(s):
            where.append("text ~* '\m%s\M'" % s.strip("\"'"))
        else:
            word_list.append(s.replace("'", "''"))

    if word_list:
        where.append("text_vector @@ plainto_tsquery('english', '%s')" \
            % ' '.join(word_list))

    if ignore_routine:
        where.append("cityhallmonitor_document.is_routine = false")

    if date_range == 'past-year':
        dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=365)
        where.append("sort_date >= '%s'" % dt)
    elif date_range == 'past-month':
        dt = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        where.append("sort_date >= '%s'" % dt)
    elif not (date_range is None or date_range == 'any' or date_range == ''):
        raise Exception('Invalid date_range parameter "%s"' \
            % date_range)

    qs = Document.objects.defer('text', 'text_vector')\
            .extra(where=where, order_by=['-sort_date'])\
            .select_related('matter_attachment', 'matter_attachment__matter')

    return qs
