# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0014_auto_20170914_1710'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donationorganization',
            name='wr_day_month',
        ),
        migrations.DeleteModel(
            name='DonationOrganization',
        ),
    ]
