# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('retail', '0004_donationorganization'),
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
