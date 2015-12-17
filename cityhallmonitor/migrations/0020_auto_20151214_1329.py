# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, models, migrations
import cityhallmonitor.models


def add_document_gin_index_wt(apps, schema_editor):
    Document = apps.get_model('cityhallmonitor', 'Document')
    db_table = Document._meta.db_table

    with connection.cursor() as c:
        sql = "CREATE INDEX cityhallmonitor_document_text_vector_wt_gin ON %s USING gin(text_vector_weighted)" \
            % db_table
        c.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0019_auto_20151211_1424'),
    ]

    operations = [
        migrations.RunPython(add_document_gin_index_wt),
    ]
