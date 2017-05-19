# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_employer_active2017'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('questionNumber', models.PositiveIntegerField(default=1, verbose_name=b'Question Number', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('questionType', models.PositiveIntegerField(verbose_name=b'Type', choices=[(1, b'Select Menu'), (2, b'Vertical Radio Buttons'), (3, b'Horizontal Radio Buttons'), (4, b'Checkboxes'), (5, b'Extended Response')])),
                ('question', models.TextField(default=b'', verbose_name=b'Question')),
                ('answer_1', models.CharField(max_length=500, null=True, verbose_name=b'Answer 1', blank=True)),
                ('answer_2', models.CharField(max_length=500, null=True, verbose_name=b'Answer 2', blank=True)),
                ('answer_3', models.CharField(max_length=500, null=True, verbose_name=b'Answer 3', blank=True)),
                ('answer_4', models.CharField(max_length=500, null=True, verbose_name=b'Answer 4', blank=True)),
                ('answer_5', models.CharField(max_length=500, null=True, verbose_name=b'Answer 5', blank=True)),
                ('answer_6', models.CharField(max_length=500, null=True, verbose_name=b'Answer 6', blank=True)),
                ('answer_7', models.CharField(max_length=500, null=True, verbose_name=b'Answer 7', blank=True)),
                ('answer_8', models.CharField(max_length=500, null=True, verbose_name=b'Answer 8', blank=True)),
                ('answer_9', models.CharField(max_length=500, null=True, verbose_name=b'Answer 9', blank=True)),
                ('answer_10', models.CharField(max_length=500, null=True, verbose_name=b'Answer 10', blank=True)),
                ('answer_11', models.CharField(max_length=500, null=True, verbose_name=b'Answer 11', blank=True)),
                ('answer_12', models.CharField(max_length=500, null=True, verbose_name=b'Answer 12', blank=True)),
                ('answer_13', models.CharField(max_length=500, null=True, verbose_name=b'Answer 13', blank=True)),
                ('answer_14', models.CharField(max_length=500, null=True, verbose_name=b'Answer 14', blank=True)),
                ('answer_15', models.CharField(max_length=500, null=True, verbose_name=b'Answer 15', blank=True)),
                ('wr_day_month', models.ForeignKey(default=0, blank=True, to='survey.Month', null=True)),
            ],
            options={
                'ordering': ('wr_day_month', 'questionNumber'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='monthlyquestion',
            unique_together=set([('wr_day_month', 'questionNumber')]),
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='questionFive',
            field=models.TextField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='questionFour',
            field=models.TextField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='questionOne',
            field=models.TextField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='questionThree',
            field=models.TextField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commutersurvey',
            name='questionTwo',
            field=models.TextField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
