# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20150419_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commutersurvey',
            name='team',
            field=smart_selects.db_fields.ChainedForeignKey(chained_model_field=b'parent', chained_field=b'employer', blank=True, auto_choose=True, to='survey.Team', null=True),
        ),
        migrations.AlterField(
            model_name='commutersurvey',
            name='work_address',
            field=models.CharField(max_length=300, verbose_name=b'Workplace address'),
        ),
        migrations.AlterField(
            model_name='leg',
            name='duration',
            field=models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MaxValueValidator(1440)]),
        ),
    ]
