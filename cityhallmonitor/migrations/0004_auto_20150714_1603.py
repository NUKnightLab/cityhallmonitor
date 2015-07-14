# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0003_matterattachment_link_obtained_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matterattachment',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]
