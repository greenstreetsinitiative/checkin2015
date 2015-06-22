# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_auto_20150520_2236'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='commutersurvey',
            unique_together=set([('email', 'wr_day_month')]),
        ),
    ]
