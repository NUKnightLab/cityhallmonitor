# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0025_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='is_routine',
            field=models.BooleanField(default=False),
        ),
    ]
