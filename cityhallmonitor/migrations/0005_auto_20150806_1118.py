# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0004_auto_20150714_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='matterattachment',
            name='doccloud_id',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='matterattachment',
            name='name',
            field=models.TextField(default='', blank=True),
        ),
    ]
