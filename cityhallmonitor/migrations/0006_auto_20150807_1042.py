# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0005_auto_20150806_1118'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventitem',
            options={'ordering': ['agenda_sequence'], 'verbose_name': 'EventItem'},
        ),
    ]
