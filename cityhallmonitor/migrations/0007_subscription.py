# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0006_auto_20150807_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('query', models.TextField()),
                ('last_check', models.DateTimeField(null=True)),
            ],
        ),
    ]
