# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0014_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matterattachment',
            name='text',
        ),
        migrations.RemoveField(
            model_name='matterattachment',
            name='text_vector',
        ),
    ]
