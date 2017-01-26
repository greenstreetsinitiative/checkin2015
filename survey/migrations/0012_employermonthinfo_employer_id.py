# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0011_employermonthinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='employermonthinfo',
            name='employer_id',
            field=models.TextField(default=b'none'),
            preserve_default=True,
        ),
    ]
