# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0008_auto_20150813_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='matter',
            name='sponsors_obtained_at',
            field=models.DateTimeField(null=True),
        ),
    ]
