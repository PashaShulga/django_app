# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-04 13:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20160704_1053'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='charts',
        #     name='grouping_by',
        #     field=models.CharField(default=datetime.datetime(2016, 7, 4, 13, 7, 11, 86105, tzinfo=utc), max_length=50),
        #     preserve_default=False,
        # ),
        # migrations.AddField(
        #     model_name='customuser',
        #     name='primary_root',
        #     field=models.BooleanField(default=False),
        # ),
        migrations.AddField(
            model_name='userdatafiles',
            name='table_name',
            field=models.CharField(default=datetime.datetime(2016, 7, 4, 13, 7, 18, 493473, tzinfo=utc), max_length=100),
            preserve_default=False,
        ),
    ]