# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0013_auto_20170906_1859'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donationorganization',
            old_name='value',
            new_name='organization_name',
        ),
        migrations.AddField(
            model_name='donationorganization',
            name='website',
            field=models.TextField(default=b'', null=True, blank=True),
            preserve_default=True,
        ),
    ]
