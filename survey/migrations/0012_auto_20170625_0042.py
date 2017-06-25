# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0011_auto_20170423_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthlyquestion',
            name='questionType',
            field=models.PositiveIntegerField(verbose_name=b'Type', choices=[(1, b'Select Menu'), (2, b'Vertical Radio Buttons'), (3, b'Horizontal Radio Buttons'), (4, b'Checkboxes'), (5, b'Extended Text Response'), (6, b'No Response')]),
        ),
    ]
