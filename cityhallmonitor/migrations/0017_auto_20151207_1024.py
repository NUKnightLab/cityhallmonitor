# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0016_auto_20151125_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='body',
        ),
        migrations.RemoveField(
            model_name='eventitem',
            name='action',
        ),
        migrations.RemoveField(
            model_name='eventitem',
            name='event',
        ),
        migrations.RemoveField(
            model_name='eventitem',
            name='matter',
        ),
        migrations.RemoveField(
            model_name='eventitem',
            name='mover',
        ),
        migrations.RemoveField(
            model_name='eventitem',
            name='seconder',
        ),
        migrations.DeleteModel(
            name='VoteType',
        ),
        migrations.CreateModel(
            name='ReadOnlyDocument',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('cityhallmonitor.document',),
        ),
        migrations.DeleteModel(
            name='Action',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='EventItem',
        ),
    ]
