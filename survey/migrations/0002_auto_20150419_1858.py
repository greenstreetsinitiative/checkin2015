# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['parent__name', 'name']},
        ),
        migrations.AlterField(
            model_name='commutersurvey',
            name='email',
            field=models.EmailField(max_length=75, verbose_name=b'Work email address'),
        ),
    ]
