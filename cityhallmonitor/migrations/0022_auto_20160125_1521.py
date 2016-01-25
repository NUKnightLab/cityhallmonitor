# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0021_person_matters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='last_check',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
    ]
