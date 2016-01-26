# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0022_auto_20160125_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='matterattachment',
            name='page_count',
            field=models.IntegerField(null=True),
        ),
    ]
