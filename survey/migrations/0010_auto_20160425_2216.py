# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0009_questionofthemonth'),
    ]

    operations = [
        migrations.AddField(
            model_name='commutersurvey',
            name='QOTM',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='questionofthemonth',
            name='value',
            field=models.CharField(max_length=400, null=True, verbose_name=b'value', blank=True),
        ),
    ]
