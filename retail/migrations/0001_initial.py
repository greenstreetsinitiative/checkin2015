# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='partner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('phone', models.CharField(max_length=32, null=True, blank=True)),
                ('website', models.CharField(max_length=2048, null=True, blank=True)),
                ('street', models.TextField()),
                ('city', models.TextField()),
                ('zipcode', models.CharField(max_length=6)),
                ('latitude', models.FloatField(default=0)),
                ('longitude', models.FloatField(default=0)),
                ('offer', models.TextField()),
                ('category', models.CharField(default=b'None', max_length=32, null=True, blank=True)),
                ('contact_name', models.TextField(null=True, blank=True)),
                ('contact_phone', models.TextField(null=True, blank=True)),
                ('contact_email', models.TextField(null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('approved', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
