# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0015_auto_20151125_1210'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='matterattachment',
            new_name='matter_attachment',
        ),
    ]
