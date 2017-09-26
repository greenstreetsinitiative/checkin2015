# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0015_auto_20170915_1623'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonationOrganization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organization_name', models.TextField(default=b'')),
                ('website', models.URLField(default=b'', null=True, verbose_name=b'Website', blank=True)),
                ('wr_day_month', models.ForeignKey(to='survey.Month', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
