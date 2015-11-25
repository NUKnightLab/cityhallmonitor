# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, models, migrations
import cityhallmonitor.models
import django.utils.timezone


def add_document_gin_index(apps, schema_editor):
    Document = apps.get_model('cityhallmonitor', 'Document')
    db_table = Document._meta.db_table

    with connection.cursor() as c:
        sql = "CREATE INDEX cityhallmonitor_document_text_vector_gin ON %s USING gin(text_vector)" \
            % db_table
        c.execute(sql)

class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0013_auto_20151123_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('matterattachment', models.OneToOneField(serialize=False, to='cityhallmonitor.MatterAttachment', primary_key=True)),
                ('sort_date', models.DateTimeField(null=True)),
                ('text', models.TextField(blank=True)),
                ('text_vector', cityhallmonitor.models.TsVectorField(null=True, editable=False, serialize=False)),
                ('is_routine', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(add_document_gin_index),
    ]
