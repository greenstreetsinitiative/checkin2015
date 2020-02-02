# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0017_auto_20200201_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='employer',
            name='active2020',
            field=models.BooleanField(default=False, verbose_name=b'2019 Challenge'),
        ),
    ]
