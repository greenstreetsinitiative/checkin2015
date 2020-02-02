# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0016_auto_20190522_0135'),
    ]

    operations = [
        migrations.AddField(
            model_name='employer',
            name='active2019',
            field=models.BooleanField(default=False, verbose_name=b'2019 Challenge'),
        ),
        migrations.AlterField(
            model_name='commutersurvey',
            name='name',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Name', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='commutersurvey',
            unique_together=set([('name', 'email', 'home_address', 'work_address', 'wr_day_month')]),
        ),
    ]
