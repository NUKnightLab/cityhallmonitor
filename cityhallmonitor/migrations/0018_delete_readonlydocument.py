# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0017_auto_20151207_1024'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReadOnlyDocument',
        ),
    ]
