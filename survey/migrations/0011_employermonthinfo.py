# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_auto_20170118_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployerMonthInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.TextField(default=b'00')),
                ('year', models.PositiveIntegerField(default=0)),
                ('dict_data', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
