# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0009_matter_sponsors_obtained_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matterattachment',
            name='doccloud_id',
        ),
    ]
