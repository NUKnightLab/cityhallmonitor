# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0002_matter_attachments_obtained_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='matterattachment',
            name='link_obtained_at',
            field=models.DateTimeField(null=True),
        ),
    ]
