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
            name='calories_total_n',
            field=models.FloatField(default=0.0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='carbon_total',
            field=models.FloatField(default=0.0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='carbon_total_driving',
            field=models.FloatField(default=0.0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='carbon_total_n',
            field=models.FloatField(default=0.0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='employer',
            name='secret_key_3',
            field=models.CharField(default=b'None', max_length=200, verbose_name=b'Secret Key'),
            preserve_default=True,
        ),
    ]
