# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0012_auto_20170625_0042'),
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
        migrations.AlterField(
            model_name='monthlyquestion',
            name='questionType',
            field=models.PositiveIntegerField(verbose_name=b'Type', choices=[(1, b'Select Menu'), (2, b'Vertical Radio Buttons'), (3, b'Horizontal Radio Buttons'), (4, b'Checkboxes'), (5, b'Extended Text Response'), (6, b'No Response'), (7, b'Single Line Text Response')]),
        ),
    ]
