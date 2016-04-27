# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0012_questionofthemonth_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionofthemonth',
            name='month',
            field=models.IntegerField(verbose_name=b'month', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)]),
        ),
    ]
