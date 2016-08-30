# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Commutersurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, verbose_name=b'Full name', blank=True)),
                ('home_address', models.CharField(max_length=300, verbose_name=b'Home address')),
                ('work_address', models.CharField(max_length=300, verbose_name=b'Work address')),
                ('email', models.EmailField(max_length=254, verbose_name=b'Work email address')),
                ('comments', models.TextField(null=True, blank=True)),
                ('share', models.BooleanField(default=False, verbose_name=b"Please don't share my identifying information with my employer")),
                ('contact', models.BooleanField(default=False, verbose_name=b'Contact me')),
                ('volunteer', models.BooleanField(default=False, verbose_name=b'Available to volunteer')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('carbon_change', models.FloatField(default=0.0, null=True, blank=True)),
                ('calorie_change', models.FloatField(default=0.0, null=True, blank=True)),
                ('change_type', models.CharField(blank=True, max_length=1, null=True, choices=[(b'p', b'Positive change'), (b'g', b'Green change'), (b'h', b'Healthy change'), (b'n', b'No change')])),
                ('already_green', models.BooleanField(default=False)),
                ('carbon_savings', models.FloatField(default=0.0, null=True, blank=True)),
                ('calories_total', models.FloatField(default=0.0, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Organization name')),
                ('nr_employees', models.PositiveIntegerField(default=1)),
                ('active2015', models.BooleanField(default=False, verbose_name=b'2015 Challenge')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Leg',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('duration', models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(1440)])),
                ('direction', models.CharField(max_length=2, choices=[(b'tw', b'to work'), (b'fw', b'from work')])),
                ('day', models.CharField(max_length=1, choices=[(b'w', b'Walk/Ride Day'), (b'n', b'Normal day')])),
                ('carbon', models.FloatField(default=0.0)),
                ('calories', models.FloatField(default=0.0)),
                ('checkin', models.ForeignKey(to='survey.Commutersurvey')),
            ],
        ),
        migrations.CreateModel(
            name='Mode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=35, verbose_name=b'Mode')),
                ('met', models.FloatField(null=True, blank=True)),
                ('carb', models.FloatField(null=True, blank=True)),
                ('speed', models.FloatField(null=True, blank=True)),
                ('green', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wr_day', models.DateField(null=True, verbose_name=b'W/R Day Date')),
                ('open_checkin', models.DateField(null=True)),
                ('close_checkin', models.DateField(null=True)),
            ],
            options={
                'ordering': ['wr_day'],
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name=b'Team')),
                ('nr_members', models.PositiveSmallIntegerField(default=1)),
                ('parent', models.ForeignKey(to='survey.Employer')),
            ],
        ),
        migrations.AddField(
            model_name='leg',
            name='mode',
            field=models.ForeignKey(to='survey.Mode'),
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='employer',
            field=models.ForeignKey(to='survey.Employer'),
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='team',
            field=models.ForeignKey(blank=True, to='survey.Team', null=True),
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='wr_day_month',
            field=models.ForeignKey(to='survey.Month'),
        ),
    ]
