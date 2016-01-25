# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0007_auto_20151123_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='employer',
            name='active2016',
            field=models.BooleanField(default=False, verbose_name=b'2016 Challenge'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='employer',
            name='nochallenge',
            field=models.BooleanField(default=False, verbose_name=b'Not In Challenge'),
            preserve_default=True,
        ),
    ]
