# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_sector_short'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commutersurvey',
            name='team',
            field=models.ForeignKey(blank=True, to='survey.Team', null=True),
        ),
    ]
