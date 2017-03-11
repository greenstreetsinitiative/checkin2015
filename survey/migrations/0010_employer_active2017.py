# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0009_questionofthemonth'),
    ]

    operations = [
        migrations.AddField(
            model_name='employer',
            name='active2017',
            field=models.BooleanField(default=False, verbose_name=b'2017 Challenge'),
            preserve_default=True,
        ),
    ]
