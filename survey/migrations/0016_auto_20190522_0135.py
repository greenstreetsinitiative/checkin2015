# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0014_employer_active2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commutersurvey',
            name='email',
            field=models.EmailField(max_length=254, verbose_name=b'Email address'),
        ),
    ]
