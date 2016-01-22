# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('retail', '0002_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='info',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='event',
            name='contact_email',
            field=models.TextField(max_length=2048, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='contact_phone',
            field=models.TextField(max_length=32, null=True, blank=True),
        ),
    ]
