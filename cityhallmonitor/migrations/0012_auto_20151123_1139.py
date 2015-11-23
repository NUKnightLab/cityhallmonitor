# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, models, migrations
import cityhallmonitor.models


def add_text_tsvector_index(apps, schema_editor):
    MatterAttachment = apps.get_model('cityhallmonitor', 'MatterAttachment')
    db_table = MatterAttachment._meta.db_table

    with connection.cursor() as c:
        sql = "CREATE INDEX cityhallmonitor_matterattachment_text_vector_gin ON %s USING gin(text_vector)" \
            % db_table
        c.execute(sql)
    

class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0011_subscription_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='matterattachment',
            name='dc_id',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='matterattachment',
            name='text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='matterattachment',
            name='text_vector',
            field=cityhallmonitor.models.TsVectorField(null=True, editable=False, serialize=False),
        ),
        migrations.RunPython(add_text_tsvector_index),
    ]
