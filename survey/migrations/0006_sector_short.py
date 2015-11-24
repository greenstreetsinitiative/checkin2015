# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_auto_20150920_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='sector',
            name='short',
            field=models.CharField(default='ab', max_length=2, verbose_name=b'Sector key'),
            preserve_default=False,
        ),
    ]
