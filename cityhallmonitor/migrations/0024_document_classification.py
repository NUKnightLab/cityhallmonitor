# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0023_matterattachment_page_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='classification',
            field=models.TextField(null=True),
        ),
    ]
