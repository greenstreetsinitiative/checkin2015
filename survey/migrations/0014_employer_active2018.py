# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0013_auto_20180123_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='employer',
            name='active2018',
            field=models.BooleanField(default=False, verbose_name=b'2018 Challenge'),
            preserve_default=True,
        ),
    ]
