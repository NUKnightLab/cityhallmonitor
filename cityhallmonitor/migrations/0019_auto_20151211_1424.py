# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cityhallmonitor.models


class Migration(migrations.Migration):

    dependencies = [
        ('cityhallmonitor', '0018_delete_readonlydocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='sponsors',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='text_vector_weighted',
            field=cityhallmonitor.models.TsVectorField(serialize=False, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='title',
            field=models.TextField(blank=True),
        ),
    ]
