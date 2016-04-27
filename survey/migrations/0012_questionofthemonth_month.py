# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0011_auto_20160426_0348'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionofthemonth',
            name='month',
            field=models.CharField(max_length=10, null=True, verbose_name=b'month', blank=True),
            preserve_default=True,
        ),
    ]
