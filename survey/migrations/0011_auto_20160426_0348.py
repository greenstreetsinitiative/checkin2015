# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_auto_20160425_2216'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commutersurvey',
            old_name='QOTM',
            new_name='question_of_the_month',
        ),
    ]
