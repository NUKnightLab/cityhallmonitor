# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0023_matterattachment_page_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='is_routine',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='document',
            name='sort_date',
            field=models.DateTimeField(null=True, db_index=True),
        ),
    ]
