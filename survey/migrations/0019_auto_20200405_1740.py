# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0018_employer_active2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employer',
            name='active2020',
            field=models.BooleanField(default=False, verbose_name=b'2020 Challenge'),
        ),
    ]
