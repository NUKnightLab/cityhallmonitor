# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0020_auto_20151214_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='matters',
            field=models.ManyToManyField(to='cityhallmonitor.Matter', through='cityhallmonitor.MatterSponsor'),
        ),
    ]
